import hashlib
import logging
import os
import plistlib
import random
import re
import time
from typing import Optional
import requests

logger = logging.getLogger(__name__)

# Apple "bag" service: returns endpoint definitions (auth URL). Required since ~2025.
BAG_URL_TEMPLATE = "https://init.itunes.apple.com/bag.xml?guid=%s"
# Apple's bag advertises the native auth endpoint, which only answers correctly when the
# path ends with "/fast/" (trailing slash). Since July 2026 that endpoint also answers
# 204/403/404/503 with an empty, non-plist body for many clients; the legacy MZFinance
# endpoint still works, but replies 302 to an assigned pod host, and the original plist
# body (with attempt=1) has to be reposted there. See majd/ipatool#513 / PR #514.
AUTH_HOST = "auth.itunes.apple.com"
DEFAULT_AUTH_URL = "https://" + AUTH_HOST + "/auth/v1/native/fast/"
LEGACY_AUTH_URL = "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate"
# Statuses that mean "this endpoint is not usable right now" when the body is not a plist.
# Apple's edge also emits bare 301/302 responses that carry no Location header at all, so
# the redirect statuses belong here too: without them a broken redirect aborts the login.
AUTH_FALLBACK_STATUSES = (204, 301, 302, 303, 307, 308, 403, 404, 429, 500, 502, 503)
# Apple throttles this endpoint by request rate, not by attempt count: measured in
# August 2026, 80 closely spaced requests got 0 usable answers, while a single request
# after two minutes of silence logged in immediately. So the backoff grows exponentially
# and is what actually matters here - hammering harder makes things strictly worse.
# Jitter keeps parallel CLI runs from lining up into a burst of their own.
AUTH_MAX_ROUNDS = int(os.environ.get("MDAST_APPSTORE_AUTH_ROUNDS", "8"))
AUTH_ROUND_BACKOFF = float(os.environ.get("MDAST_APPSTORE_AUTH_BACKOFF", "20"))
AUTH_MAX_BACKOFF = float(os.environ.get("MDAST_APPSTORE_AUTH_MAX_BACKOFF", "150"))
AUTH_BACKOFF_JITTER = 5.0
AUTH_MAX_REDIRECTS = 4
BUY_DOMAIN = "buy.itunes.apple.com"


def _normalize_auth_endpoint(endpoint):
    """Add the trailing slash the native auth endpoint requires.

    Apple's bag returns ".../auth/v1/native/fast"; posting without the trailing slash
    gets a 301/204 with an HTML or empty body that the plist parser chokes on
    (majd/ipatool#507). The legacy MZFinance endpoint is left untouched.
    """
    if endpoint and "/native/" in endpoint and not endpoint.endswith("/"):
        return endpoint + "/"
    return endpoint


class _AuthEndpointUnusable(Exception):
    """Raised internally when an auth endpoint should be retried elsewhere."""

    def __init__(self, status_code, detail=""):
        self.status_code = status_code
        self.detail = detail
        super().__init__("auth endpoint unusable (HTTP %s) %s" % (status_code, detail))


# buyProduct lives on MZFinance, not MZBuy: the MZBuy variant answers HTTP 200 with
# m-allowed=False / cancel-purchase-batch=True ("Unable to process your request.") for
# every app, so no license is ever created and the download that follows fails with
# failureType 9610. Verified against Apple in August 2026; ipatool uses the same path.
PURCHASE_PATH = "/WebObjects/MZFinance.woa/wa/buyProduct"
DOWNLOAD_PATH = "/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"

# Apple failure types (mirrors ipatool pkg/appstore/constants.go).
FAILURE_INVALID_CREDENTIALS = '-5000'
FAILURE_DEVICE_VERIFICATION_FAILED = '1008'
FAILURE_PASSWORD_TOKEN_EXPIRED = '2034'
FAILURE_SIGN_IN_REQUIRED = '2042'
FAILURE_TEMPORARILY_UNAVAILABLE = '2059'
FAILURE_LICENSE_ALREADY_EXISTS = '5002'
FAILURE_LICENSE_NOT_FOUND = '9610'
# Failure types that mean "the session went stale, log in again and retry".
FAILURES_NEEDING_REAUTH = (
    FAILURE_DEVICE_VERIFICATION_FAILED,
    FAILURE_PASSWORD_TOKEN_EXPIRED,
    FAILURE_SIGN_IN_REQUIRED,
)
# 5002 is context dependent: on buyProduct it means the account already owns the app
# (success), but on volumeStoreDownloadProduct Apple reuses it for a stale session and
# only a fresh login clears it. ipatool maps it the same way (majd/ipatool#468).
FAILURES_NEEDING_REAUTH_ON_DOWNLOAD = FAILURES_NEEDING_REAUTH + (FAILURE_LICENSE_ALREADY_EXISTS,)

from mdast_cli.distribution_systems.appstore_client.schemas.store_authenticate_req import StoreAuthenticateReq
from mdast_cli.distribution_systems.appstore_client.schemas.store_authenticate_resp import StoreAuthenticateResp
from mdast_cli.distribution_systems.appstore_client.schemas.store_buyproduct_req import StoreBuyproductReq
from mdast_cli.distribution_systems.appstore_client.schemas.store_download_req import StoreDownloadReq
from mdast_cli.distribution_systems.appstore_client.schemas.store_download_resp import StoreDownloadResp

# User-Agent aligned with ipatool post-PR #316 (Apple API compatibility)
APPSTORE_USER_AGENT = (
    "Configurator/2.17 (Macintosh; OS X 15.2; 24C5089c) AppleWebKit/0620.1.16.11.6"
)


class StoreException(Exception):
    def __init__(self, req, err_msg, err_type=None):
        self.req = req
        self.err_msg = err_msg
        self.err_type = err_type
        super().__init__(
            "Store %s error: %s" % (self.req, self.err_msg) if not self.err_type else
            "Store %s error: %s, errorType: %s" % (self.req, self.err_msg, self.err_type)
        )


def _parse_bag_response(content: bytes) -> Optional[str]:
    """Extract authenticateAccount URL from Apple bag plist/XML. Returns None if not found."""
    if not content or len(content) < 10:
        return None
    # Try direct plist parse (binary or XML)
    try:
        data = plistlib.loads(content)
        if isinstance(data, dict):
            # 'authenticateAccount' moved to the bag root (majd/ipatool#486); older bags
            # keep it under 'urlBag'. Check the root first, then fall back to urlBag.
            endpoint = data.get("authenticateAccount") or data.get("authenticate")
            if not endpoint:
                url_bag = data.get("urlBag") or data.get("URLBag")
                if isinstance(url_bag, dict):
                    endpoint = url_bag.get("authenticateAccount") or url_bag.get("authenticate")
            return endpoint
        return None
    except Exception:
        pass
    # Try XML: unwrap Document and find plist/dict (ipatool-style normalization)
    try:
        text = content.decode("utf-8", errors="replace")
        # Extract inner body of <Document>...</Document>
        doc_match = re.search(r"<Document\b[^>]*>(.*)</Document>", text, re.DOTALL | re.IGNORECASE)
        if doc_match:
            text = doc_match.group(1).strip()
        # Find <key>authenticateAccount</key><string>URL</string> or similar
        key_match = re.search(
            r"<key>\s*authenticateAccount\s*</key>\s*<string>([^<]+)</string>",
            text,
            re.IGNORECASE,
        )
        if key_match:
            return key_match.group(1).strip()
        # Fallback: any key with "authenticate" and string value
        for m in re.finditer(r"<key>\s*([^<]+)\s*</key>\s*<string>([^<]+)</string>", text):
            if "authenticate" in m.group(1).lower():
                return m.group(2).strip()
    except Exception:
        pass
    return None


def _log_response_on_plist_error(r: requests.Response, context: str) -> None:
    """Log raw response details when plist parsing fails (e.g. HTML error page)."""
    content = r.content
    content_type = r.headers.get("Content-Type", "")
    logger.warning(
        "Plist parse failed for %s: status=%s, Content-Type=%r, body_len=%s",
        context,
        r.status_code,
        content_type,
        len(content),
    )
    if content:
        try:
            preview = content[:500].decode("utf-8", errors="replace")
            if "\n" in preview:
                preview = preview.split("\n")[0][:200]
            logger.warning("Response body preview (first 200 chars): %s", preview[:200])
        except Exception:
            logger.warning("Response body (first 100 bytes repr): %r", content[:100])
    else:
        logger.warning("Response body is empty")


class StoreClient(object):
    def __init__(self, sess: requests.Session, guid: str = None):
        self.sess = sess
        self.guid = guid
        self.dsid = None
        self.store_front = None
        self.account_name = None
        self.pod = None  # Pod from auth response; used for purchase/download host (e.g. p25-buy.)

    def get_bag(self) -> str:
        """Fetch Apple bag and return auth endpoint URL (required since Apple changed endpoints)."""
        url = BAG_URL_TEMPLATE % self.guid
        r = self.sess.get(
            url,
            headers={"Accept": "application/xml", "User-Agent": APPSTORE_USER_AGENT},
            verify=False,
            timeout=30,
        )
        if r.status_code != 200:
            logger.warning(
                "Bag request failed: status=%s, falling back to default auth URL",
                r.status_code,
            )
            return DEFAULT_AUTH_URL
        auth_endpoint = _normalize_auth_endpoint(_parse_bag_response(r.content))
        if auth_endpoint:
            logger.debug("Using auth endpoint from bag: %s", auth_endpoint[:60] + "...")
            return auth_endpoint
        logger.warning("Could not parse bag response, falling back to default auth URL")
        return DEFAULT_AUTH_URL

    def _post_authenticate(self, url, appleId, password, attempt):
        req = StoreAuthenticateReq(
            appleId=appleId,
            password=password,
            attempt=str(attempt),
            createSession=None,
            guid=self.guid,
            rmp='0',
            why='signIn',
        )
        return self.sess.post(
            url,
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": APPSTORE_USER_AGENT,
            },
            data=plistlib.dumps(req.as_dict()),
            allow_redirects=False,
            verify=False,
            timeout=60,
        )

    def _authenticate_at(self, auth_url, appleId, password):
        """Authenticate against a single endpoint, following Apple's pod redirect.

        The legacy endpoint answers 302 with a Location pointing at the account's pod
        (e.g. https://p7-buy.itunes.apple.com/...?Pod=7&PRH=7). The original plist body
        must be reposted there unchanged - in particular attempt stays 1, otherwise Apple
        rejects the request (majd/ipatool#514).
        """
        url = auth_url
        attempt = 1
        redirects = 0
        r = None
        while True:
            r = self._post_authenticate(url, appleId, password, attempt)
            if r.status_code in (301, 302, 303, 307, 308) and r.headers.get('Location'):
                redirects += 1
                if redirects > AUTH_MAX_REDIRECTS:
                    raise _AuthEndpointUnusable(r.status_code, "too many redirects")
                url = r.headers['Location']
                logger.debug("Auth redirected to pod endpoint: %s", url)
                continue  # attempt is intentionally NOT incremented here
            try:
                resp = StoreAuthenticateResp.from_dict(plistlib.loads(r.content))
            except plistlib.InvalidFileException:
                _log_response_on_plist_error(r, "authenticate")
                raise _AuthEndpointUnusable(r.status_code, "non-plist body") from None
            if resp.m_allowed:
                return r, resp
            # Apple sometimes rejects the very first attempt with an invalid-credentials
            # failure; a single retry with attempt=2 clears it (ipatool does the same).
            if attempt == 1 and str(resp.failureType) == '-5000':
                attempt = 2
                continue
            raise StoreException("authenticate", resp.customerMessage, resp.failureType)

    def authenticate(self, appleId, password):
        if not self.guid:
            self.guid = self._generateGuid(appleId)

        endpoints = []
        for candidate in (self.get_bag(), DEFAULT_AUTH_URL, LEGACY_AUTH_URL):
            if candidate and candidate not in endpoints:
                endpoints.append(candidate)

        last_failure = None
        for round_no in range(1, AUTH_MAX_ROUNDS + 1):
            for auth_url in endpoints:
                try:
                    r, resp = self._authenticate_at(auth_url, appleId, password)
                    self._store_auth_result(r, resp, auth_url)
                    return resp
                except _AuthEndpointUnusable as e:
                    if e.status_code not in AUTH_FALLBACK_STATUSES:
                        raise StoreException(
                            "authenticate",
                            "Server response is not valid plist (HTTP %s). See log for details."
                            % e.status_code,
                            None,
                        ) from e
                    last_failure = e
                    logger.warning(
                        "Auth endpoint %s unusable (HTTP %s, %s), trying next endpoint",
                        auth_url, e.status_code, e.detail,
                    )
            if round_no < AUTH_MAX_ROUNDS:
                delay = min(AUTH_ROUND_BACKOFF * (2 ** (round_no - 1)), AUTH_MAX_BACKOFF)
                delay += random.uniform(0, AUTH_BACKOFF_JITTER)
                logger.info(
                    "All App Store auth endpoints failed (round %s/%s), waiting %.0fs before "
                    "retrying - Apple throttles by request rate, so backing off is what helps",
                    round_no, AUTH_MAX_ROUNDS, delay,
                )
                time.sleep(delay)

        raise StoreException(
            "authenticate",
            "Apple rejected every authentication endpoint (last status: HTTP %s). "
            "This is an Apple-side/network block rather than a credentials problem: "
            "retry later or from a different egress IP (see majd/ipatool#513)."
            % (last_failure.status_code if last_failure else "unknown"),
            None,
        )

    def _store_auth_result(self, r, resp, auth_url):
        self.sess.headers['X-Dsid'] = self.sess.headers['iCloud-Dsid'] = str(resp.download_queue_info.dsid)
        store_front = r.headers.get('x-set-apple-store-front')
        if store_front:
            self.sess.headers['X-Apple-Store-Front'] = store_front
            self.store_front = store_front
        self.sess.headers['X-Token'] = resp.passwordToken
        self.dsid = resp.download_queue_info.dsid

        pod_header = r.headers.get("pod") or r.headers.get("Pod")
        if pod_header:
            self.pod = pod_header.strip()
        else:
            # The pod redirect lands on e.g. https://p7-buy.itunes.apple.com/...?Pod=7
            match = re.search(r"https?://p(\d+)-" + re.escape(BUY_DOMAIN), r.url or auth_url)
            self.pod = match.group(1) if match else None
        if self.pod:
            logger.debug("Using pod for buy host: %s", self.pod)

        self.account_name = resp.accountInfo.address.firstName + " " + resp.accountInfo.address.lastName

    def _buy_host(self) -> str:
        """Host for purchase/download (pod-specific if set)."""
        if self.pod:
            return "p" + self.pod + "-" + BUY_DOMAIN
        return BUY_DOMAIN

    def find_app(self, app_id=None, bundle_id=None, country="US"):
        return self.sess.get("https://itunes.apple.com/lookup?",
                             params={
                                 "bundleId": bundle_id,
                                 "id": app_id,
                                 "term": None,
                                 "country": country,
                                 "limit": 1,
                                 "media": "software",
                             },
                             headers={
                                 "Content-Type": "application/x-www-form-urlencoded",
                             },
                             verify=False)

    def purchase(self, app_id, productType='C', pricingParameters='STDQ'):
        """Acquire a license for the app.

        Returns True when a new license was created, False when the account already
        owned it. Raises StoreException when Apple refuses - notably the response is a
        HTTP 200 either way, so the plist has to be inspected rather than the status.
        """
        url = "https://%s%s" % (self._buy_host(), PURCHASE_PATH)
        req = StoreBuyproductReq(
            guid=self.guid,
            salableAdamId=str(app_id),
            appExtVrsId='0',

            price='0',
            productType=productType,
            pricingParameters=pricingParameters,

            hasAskedToFulfillPreorder='true',
            buyWithoutAuthorization='true',
            hasDoneAgeCheck='true',
        )

        r = self.sess.post(
            url,
            headers={
                "Content-Type": "application/x-apple-plist",
                "User-Agent": APPSTORE_USER_AGENT,
            },
            data=plistlib.dumps(req.as_dict()),
            verify=False,
            timeout=60,
        )
        logger.debug("buyProduct response: status=%s, content_length=%s", r.status_code, len(r.content))

        try:
            data = plistlib.loads(r.content)
        except plistlib.InvalidFileException as e:
            _log_response_on_plist_error(r, "buyProduct")
            raise StoreException(
                "buyProduct", "Server response is not valid plist. See log for response details.", None,
            ) from e

        failure_type = str(data.get('failureType') or '')
        message = data.get('customerMessage') or ''

        # Apple reports "already owned" either as failureType 5002 or as a bare HTTP 500.
        if failure_type == FAILURE_LICENSE_ALREADY_EXISTS or r.status_code == 500:
            logger.info('App is already licensed for this Apple ID')
            return False
        if failure_type or data.get('cancel-purchase-batch') or data.get('m-allowed') is False:
            logger.warning(
                "buyProduct rejected: failureType=%r, customerMessage=%r, app_id=%s",
                failure_type, message, app_id,
            )
            raise StoreException('buyProduct', message or 'failed to purchase app', failure_type or None)
        if data.get('jingleDocType') != 'purchaseSuccess' or data.get('status') != 0:
            raise StoreException('buyProduct', message or 'failed to purchase app', failure_type or None)

        return True

    def download(self, app_id, app_ver_id=""):
        req = StoreDownloadReq(creditDisplay="", guid=self.guid, salableAdamId=app_id, appExtVrsId=app_ver_id)
        download_url = "https://%s%s?guid=%s" % (self._buy_host(), DOWNLOAD_PATH, self.guid)
        r = self.sess.post(
            download_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": APPSTORE_USER_AGENT,
            },
            data=plistlib.dumps(req.as_dict()),
            verify=False,
        )

        logger.debug(
            "volumeStoreDownloadProduct response: status=%s, content_length=%s",
            r.status_code,
            len(r.content),
        )
        try:
            resp = StoreDownloadResp.from_dict(plistlib.loads(r.content))
        except plistlib.InvalidFileException as e:
            _log_response_on_plist_error(r, "volumeStoreDownloadProduct")
            raise StoreException(
                "volumeStoreDownloadProduct",
                "Server response is not valid plist. See log for response details.",
                None,
            ) from e
        failure_type = str(resp.failureType or '')
        # No songList means no download info, whatever the HTTP status says. Surface
        # Apple's own failure type so callers can react: 9610 means the account holds no
        # license for the app (buy it first), 1008/2034/2042 mean the session went stale.
        if resp.cancel_purchase_batch or failure_type or not resp.songList:
            logger.warning(
                "App Store download rejected: customerMessage=%r, failureType=%r, app_id=%s",
                resp.customerMessage,
                resp.failureType,
                app_id,
            )
            raise StoreException(
                "volumeStoreDownloadProduct",
                resp.customerMessage or 'Apple returned no download info for this app',
                failure_type or None,
            )
        return resp

    def _generateGuid(self, appleId):
        DEFAULT_GUID = '123C2941396B'
        GUID_DEFAULT_PREFIX = 2
        GUID_SEED = 'STINGRAY'
        GUID_POS = 10

        h = hashlib.sha1((GUID_SEED + appleId + GUID_SEED).encode("utf-8")).hexdigest()
        defaultPart = DEFAULT_GUID[:GUID_DEFAULT_PREFIX]
        hashPart = h[GUID_POS: GUID_POS + (len(DEFAULT_GUID) - GUID_DEFAULT_PREFIX)]
        guid = (defaultPart + hashPart).upper()
        return guid
