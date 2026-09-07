import hashlib
import logging
import os
import plistlib
import re
import time
import requests
from requests.adapters import HTTPAdapter
from mdast_cli.distribution_systems.appstore_client.sap import SAPError, SAPSigner, parse_bag, validate_endpoint

logger = logging.getLogger(__name__)

BAG_URL_TEMPLATE = "https://init.itunes.apple.com/bag.xml?guid=%s"
LEGACY_AUTH_URL = "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate"
AUTH_MAX_REDIRECTS = 4
BUY_DOMAIN = "buy.itunes.apple.com"


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
# (success), while on volumeStoreDownloadProduct Apple throws it at random. Measured in
# August 2026 over one session: attempt 1 failed for two apps, attempts 2-4 succeeded for
# both, attempt 5 failed again for one of them - and a fresh login (13 minutes of auth
# backoff) did not clear it. So it is retried in place rather than treated as a stale
# session the way ipatool does (majd/ipatool#468); re-authenticating costs minutes and
# does not help.
DOWNLOAD_RETRY_FAILURES = (FAILURE_LICENSE_ALREADY_EXISTS,)
DOWNLOAD_MAX_ATTEMPTS = int(os.environ.get("MDAST_APPSTORE_DOWNLOAD_ATTEMPTS", "5"))
DOWNLOAD_RETRY_PAUSE = float(os.environ.get("MDAST_APPSTORE_DOWNLOAD_PAUSE", "6"))

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

    def get_bag(self):
        response = self.sess.get(
            BAG_URL_TEMPLATE % self.guid,
            headers={"Accept": "application/xml", "User-Agent": APPSTORE_USER_AGENT},
            verify=True, timeout=30,
        )
        if response.status_code != 200:
            raise SAPError("Apple bag request failed (HTTP %s)" % response.status_code)
        try:
            content = response.content
            # Apple also wraps its plist in an outer Document element.
            if b"<Document" in content:
                match = re.search(rb"<plist\b.*?</plist>", content, re.DOTALL)
                if match:
                    content = match.group(0)
            return parse_bag(plistlib.loads(content))
        except (ValueError, TypeError, plistlib.InvalidFileException):
            raise SAPError("Apple bag is not a valid SAP configuration") from None

    def _post_authenticate(self, url, appleId, password, attempt, signer):
        validate_endpoint(url, authentication=True)
        req = StoreAuthenticateReq(
            appleId=appleId, password=password, attempt=str(attempt),
            createSession=None, guid=self.guid, rmp='0', why='signIn',
        )
        body = plistlib.dumps(req.as_dict())
        signature = signer.sign(body)
        # Signed POST retries are handled explicitly below, including re-signing.
        # A general-purpose caller may have enabled urllib3 POST retries.
        self.sess.mount(url.split('?')[0], HTTPAdapter(max_retries=0))
        return self.sess.post(
            url,
            headers={
                "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": APPSTORE_USER_AGENT,
                "X-Apple-ActionSignature": signature,
            },
            data=body, allow_redirects=False, verify=True, timeout=60,
        )

    def _authenticate_at(self, auth_url, appleId, password, signer):
        url, attempt, redirects, transient = auth_url, 1, 0, 0
        while True:
            response = self._post_authenticate(url, appleId, password, attempt, signer)
            status = response.status_code
            logger.info("App Store signed authentication response: HTTP %s", status)
            if status in (301, 302, 303, 307, 308):
                location = response.headers.get('Location')
                if not location:
                    raise StoreException('authenticate', 'Apple redirect has no Location (HTTP %s)' % status)
                validate_endpoint(location, authentication=True)
                redirects += 1
                if redirects > AUTH_MAX_REDIRECTS:
                    raise StoreException('authenticate', 'Too many Apple authentication redirects')
                url = location
                continue
            try:
                data = plistlib.loads(response.content)
                if not isinstance(data, dict):
                    raise ValueError
            except (ValueError, TypeError, plistlib.InvalidFileException):
                transient += 1
                if (status in (204, 404) or status >= 500) and transient < 3:
                    time.sleep(0.25 * transient)
                    continue
                raise StoreException('authenticate', 'Apple returned a non-plist authentication response (HTTP %s)' % status) from None
            resp = StoreAuthenticateResp.from_dict(data)
            # Both response shapes are in use: older clients read download-queue-info.
            dsid = data.get('dsPersonId') or (data.get('download-queue-info') or {}).get('dsid')
            if status == 200 and resp.passwordToken and dsid and not resp.failureType:
                if not resp.download_queue_info:
                    resp = StoreAuthenticateResp.from_dict(dict(data, **{'download-queue-info': {'dsid': dsid}}))
                return response, resp
            if attempt == 1 and str(resp.failureType) == '-5000':
                attempt = 2
                transient = 0
                continue
            raise StoreException('authenticate', resp.customerMessage or 'Apple rejected authentication', resp.failureType)

    def authenticate(self, appleId, password):
        if not self.guid:
            self.guid = self._generateGuid(appleId)
        try:
            config = self.get_bag()
            with SAPSigner(config, self.guid) as signer:
                response, result = self._authenticate_at(config['auth_url'], appleId, password, signer)
            self._store_auth_result(response, result, config['auth_url'])
            return result
        except SAPError as exc:
            raise StoreException('authenticate', str(exc), 'sap') from exc

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

        address = getattr(resp.accountInfo, 'address', None)
        self.account_name = " ".join(filter(None, (
            getattr(address, 'firstName', None), getattr(address, 'lastName', None),
        )))

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
