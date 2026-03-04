import hashlib
import logging
import plistlib
import re

import requests

logger = logging.getLogger(__name__)

# Apple "bag" service: returns endpoint definitions (auth URL). Required since ~2025.
BAG_URL_TEMPLATE = "https://init.itunes.apple.com/bag.xml?guid=%s"
DEFAULT_AUTH_URL_TEMPLATE = "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?guid=%s"
BUY_DOMAIN = "buy.itunes.apple.com"
PURCHASE_PATH = "/WebObjects/MZBuy.woa/wa/buyProduct"
DOWNLOAD_PATH = "/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"

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


def _parse_bag_response(content: bytes) -> str | None:
    """Extract authenticateAccount URL from Apple bag plist/XML. Returns None if not found."""
    if not content or len(content) < 10:
        return None
    # Try direct plist parse (binary or XML)
    try:
        data = plistlib.loads(content)
        if isinstance(data, dict):
            url_bag = data.get("urlBag") or data.get("URLBag")
            if isinstance(url_bag, dict):
                return url_bag.get("authenticateAccount") or url_bag.get("authenticate")
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
            return DEFAULT_AUTH_URL_TEMPLATE % self.guid
        auth_endpoint = _parse_bag_response(r.content)
        if auth_endpoint:
            logger.debug("Using auth endpoint from bag: %s", auth_endpoint[:60] + "...")
            return auth_endpoint
        logger.warning("Could not parse bag response, falling back to default auth URL")
        return DEFAULT_AUTH_URL_TEMPLATE % self.guid

    def authenticate(self, appleId, password):
        if not self.guid:
            self.guid = self._generateGuid(appleId)
        auth_url = self.get_bag()
        max_attempts = 4
        attempt = 1
        r = None
        while attempt <= max_attempts:
            req = StoreAuthenticateReq(
                appleId=appleId,
                password=password,
                attempt=str(attempt),
                createSession=None,
                guid=self.guid,
                rmp='0',
                why='signIn',
            )
            r = self.sess.post(
                auth_url,
                headers={
                    "Accept": "*/*",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": APPSTORE_USER_AGENT,
                },
                data=plistlib.dumps(req.as_dict()),
                allow_redirects=False,
                verify=False,
            )
            if r.status_code == 302:
                auth_url = r.headers.get('Location')
                if not auth_url:
                    raise StoreException("authenticate", "Missing Location header on redirect", None)
                attempt += 1
                continue
            break
        if r is None or r.status_code == 302:
            raise StoreException("authenticate", "Too many redirects", None)
        try:
            resp = StoreAuthenticateResp.from_dict(plistlib.loads(r.content))
        except plistlib.InvalidFileException as e:
            _log_response_on_plist_error(r, "authenticate")
            raise StoreException(
                "authenticate",
                "Server response is not valid plist (possibly HTML error page or empty). See log for response details.",
                None,
            ) from e
        if not resp.m_allowed:
            raise StoreException("authenticate", resp.customerMessage, resp.failureType)

        self.sess.headers['X-Dsid'] = self.sess.headers['iCloud-Dsid'] = str(resp.download_queue_info.dsid)
        self.sess.headers['X-Apple-Store-Front'] = r.headers.get('x-set-apple-store-front')
        self.sess.headers['X-Token'] = resp.passwordToken
        pod_header = r.headers.get("pod") or r.headers.get("Pod")
        if pod_header:
            self.pod = pod_header.strip()
        else:
            # Auth URL from bag may be e.g. https://p25-buy.itunes.apple.com/... — extract pod
            match = re.search(r"^https?://p(\d+)-" + re.escape(BUY_DOMAIN), auth_url)
            self.pod = match.group(1) if match else None
        if self.pod:
            logger.debug("Using pod for buy host: %s", self.pod)

        self.account_name = resp.accountInfo.address.firstName + " " + resp.accountInfo.address.lastName
        return resp

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

    def purchase(self, app_id, productType='C'):
        url = "https://%s%s" % (self._buy_host(), PURCHASE_PATH)
        req = StoreBuyproductReq(
            guid=self.guid,
            salableAdamId=str(app_id),
            appExtVrsId='0',

            price='0',
            productType=productType,
            pricingParameters='STDQ',

            hasAskedToFulfillPreorder='true',
            buyWithoutAuthorization='true',
            hasDoneAgeCheck='true',
        )
        payload = req.as_dict()

        return self.sess.post(
            url,
            headers={
                "Content-Type": "application/x-apple-plist",
                "User-Agent": APPSTORE_USER_AGENT,
            },
            data=plistlib.dumps(payload),
            verify=False,
        )

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
        if resp.cancel_purchase_batch:
            logger.warning(
                "App Store download rejected: customerMessage=%r, failureType=%r, app_id=%s",
                resp.customerMessage,
                resp.failureType,
                app_id,
            )
            raise StoreException(
                "volumeStoreDownloadProduct", resp.customerMessage, resp.failureType
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
