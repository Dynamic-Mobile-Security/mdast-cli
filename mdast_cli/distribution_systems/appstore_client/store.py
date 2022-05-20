import plistlib

import requests

from .schemas.store_authenticate_req import StoreAuthenticateReq
from .schemas.store_authenticate_resp import StoreAuthenticateResp
from .schemas.store_download_req import StoreDownloadReq
from .schemas.store_download_resp import StoreDownloadResp
from .schemas.store_buyproduct_req import StoreBuyproductReq
from .schemas.store_buyproduct_resp import StoreBuyproductResp
from mdast_cli.helpers.logging import Log


class StoreException(Exception):
    def __init__(self, req, err_msg, err_type=None):
        self.req = req
        self.err_msg = err_msg
        self.err_type = err_type
        super().__init__(
            "Store %s error: %s" % (self.req, self.err_msg) if not self.err_type else
            "Store %s error: %s, errorType: %s" % (self.req, self.err_msg, self.err_type)
        )


class StoreClient(object):
    def __init__(self, sess: requests.Session, guid: str = '000C2941396B'):
        self.sess = sess
        self.guid = guid
        self.dsid = None
        self.store_front = None
        self.account_name = None

    def authenticate(self, appleId, password):
        req = StoreAuthenticateReq(appleId=appleId, password=password, attempt='4', createSession="true",
                                   guid=self.guid, rmp='0', why='signIn')
        url = "https://p46-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate?guid=%s" % self.guid
        while True:
            r = self.sess.post(url,
                               headers={
                                   "Accept": "*/*",
                                   "Content-Type": "application/x-www-form-urlencoded",
                                   "User-Agent":
                                       "Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8",
                               }, data=plistlib.dumps(req.as_dict()), allow_redirects=False)
            if r.status_code == 302:
                url = r.headers['Location']
                continue
            break
        resp = StoreAuthenticateResp.from_dict(plistlib.loads(r.content))
        if not resp.m_allowed:
            raise StoreException("authenticate", resp.customerMessage, resp.failureType)

        self.sess.headers['X-Dsid'] = self.sess.headers['iCloud-Dsid'] = str(resp.download_queue_info.dsid)
        self.sess.headers['X-Apple-Store-Front'] = r.headers.get('x-set-apple-store-front')
        self.sess.headers['X-Token'] = resp.passwordToken

        self.account_name = resp.accountInfo.address.firstName + " " + resp.accountInfo.address.lastName
        return resp

    def find_app_by_bundle(self, bundleId, appId=None, term=None, country="US", limit=1, media="software"):
        return self.sess.get("https://itunes.apple.com/lookup?",
                             params={
                                 "bundleId": bundleId,
                                 "id": appId,
                                 "term": term,
                                 "country": country,
                                 "limit": limit,
                                 "media": media,
                             },
                             headers={
                                 "Content-Type": "application/x-www-form-urlencoded",
                             })

    def purchase(self, appId, productType='C'):
        url = "https://buy.itunes.apple.com/WebObjects/MZBuy.woa/wa/buyProduct"
        req = StoreBuyproductReq(
            guid=self.guid,
            salableAdamId=str(appId),
            appExtVrsId='0',

            price='0',
            productType=productType,
            pricingParameters='STDQ',

            hasAskedToFulfillPreorder='true',
            buyWithoutAuthorization='true',
            hasDoneAgeCheck='true',
        )
        payload = req.as_dict()

        return self.sess.post(url,
                              headers={
                                  "Content-Type": "application/x-apple-plist",
                                  "User-Agent": "Configurator/2.15 (Macintosh; OS X 11.0.0; 16G29) AppleWebKit/2603.3.8",
                              },
                              data=plistlib.dumps(payload))

    def download(self, app_id, app_ver_id=""):
        req = StoreDownloadReq(creditDisplay="", guid=self.guid, salableAdamId=app_id, appExtVrsId=app_ver_id)
        r = self.sess.post("https://p25-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct",
                           params={
                               "guid": self.guid
                           },
                           headers={
                               "Content-Type": "application/x-www-form-urlencoded",
                               "User-Agent": "Configurator/2.0 (Macintosh; OS X 10.12.6; 16G29) AppleWebKit/2603.3.8",
                           }, data=plistlib.dumps(req.as_dict()))

        resp = StoreDownloadResp.from_dict(plistlib.loads(r.content))
        if resp.cancel_purchase_batch:
            raise StoreException("volumeStoreDownloadProduct", resp, resp.customerMessage,
                                 resp.failureType + '-' + resp.metrics.dialogId)
        return resp
