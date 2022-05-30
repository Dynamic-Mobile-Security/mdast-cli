import ssl
import sys
from base64 import b64decode, urlsafe_b64encode

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives.serialization import load_der_public_key
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

from mdast_cli.helpers.logging import Log

from . import config, googleplay_pb2, utils

ssl_verify = True

BASE = "https://android.clients.google.com/"
FDFE = BASE + "fdfe/"
CHECKIN_URL = BASE + "checkin"
AUTH_URL = BASE + "auth"

UPLOAD_URL = FDFE + "uploadDeviceConfig"
DETAILS_URL = FDFE + "details"
DELIVERY_URL = FDFE + "delivery"
PURCHASE_URL = FDFE + "purchase"

CONTENT_TYPE_URLENC = "application/x-www-form-urlencoded; charset=UTF-8"
CONTENT_TYPE_PROTO = "application/x-protobuf"


def encrypt_password(login, passwd):
    binaryKey = b64decode(config.GOOGLE_PUBKEY)
    i = utils.readInt(binaryKey, 0)
    modulus = utils.toBigInt(binaryKey[4:][0:i])
    j = utils.readInt(binaryKey, i + 4)
    exponent = utils.toBigInt(binaryKey[i + 8:][0:j])

    digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
    digest.update(binaryKey)
    h = b'\x00' + digest.finalize()[0:4]

    der_data = encode_dss_signature(modulus, exponent)
    publicKey = load_der_public_key(der_data, backend=default_backend())

    to_be_encrypted = login.encode() + b'\x00' + passwd.encode()
    ciphertext = publicKey.encrypt(
        to_be_encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

    return urlsafe_b64encode(h + ciphertext)


class SSLContext(ssl.SSLContext):
    def set_alpn_protocols(self, protocols):
        """
        ALPN headers cause Google to return 403 Bad Authentication.
        """
        pass


class AuthHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        """
        Secure settings from ssl.create_default_context(), but without
        ssl.OP_NO_TICKET which causes Google to return 403 Bad
        Authentication.
        """
        context = SSLContext()
        context.set_ciphers(ssl_.DEFAULT_CIPHERS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.options &= ~0x4000
        self.poolmanager = PoolManager(*args, ssl_context=context, **kwargs)


class GooglePlayAPI(object):
    def __init__(self, locale="en_US", timezone="UTC", device_codename="walleye", proxies_config=None):
        self.authSubToken = None
        self.gsfId = None
        self.device_config_token = None
        self.deviceCheckinConsistencyToken = None
        self.dfeCookie = None
        self.proxies_config = proxies_config
        self.deviceBuilder = config.DeviceBuilder(device_codename)
        self.deviceBuilder.setLocale(locale)
        self.deviceBuilder.setTimezone(timezone)
        self.session = requests.session()
        self.session.mount('https://', AuthHTTPAdapter())

    def login(self, email, password, gsfId, authSubToken):
        if email is not None and password is not None:
            Log.info('Google Play - Logging in with email and password, you should copy token after')
            encryptedPass = encrypt_password(email, password).decode('utf-8')
            params = self.deviceBuilder.getLoginParams(email, encryptedPass)
            params['service'] = 'ac2dm'
            params['add_account'] = '1'
            params['callerPkg'] = 'com.google.android.gms'
            headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
            headers['app'] = 'com.google.android.gsm'
            with requests.Session() as s:
                s.headers = {'User-Agent': 'GoogleAuth/1.4'}
                response = s.post(AUTH_URL,
                                  data=params,
                                  verify=ssl_verify)
            data = response.text.split()
            params = {}
            for d in data:
                if "=" not in d:
                    continue
                k, v = d.split("=", 1)
                params[k.strip().lower()] = v.strip()
            if params["auth"] != '':
                ac2dmToken = params["auth"]
            elif "error" in params:
                if "NeedsBrowser" in params["error"]:
                    Log.error('Google Play - Security check is needed, '
                              'try to visit https://accounts.google.com/b/0/DisplayUnlockCaptcha to unlock.')
                    Log.error(f'Google Play - server says: "{params["error"]}"')
                    sys.exit(4)

            self.gsfId = self.checkin(email, ac2dmToken)
            self.getAuthSubToken(email, encryptedPass)
            self.uploadDeviceConfig()
            Log.info(f'Google Play - gsfId: {self.gsfId}, authSubToken: {self.authSubToken}')
            Log.info(f'Google Play - You should copy these parameters and use them for next scans instead '
                     f'of email and password:')
            Log.info(f'Google Play - "--google_play_gsfid {self.gsfId} --google_play_auth_token {self.authSubToken}"')
        elif gsfId is not None and authSubToken is not None:
            self.gsfId = gsfId
            self.setAuthSubToken(authSubToken)
            Log.info('Google Play - Logging in with gsfid and auth token')
        else:
            Log.error('Google Play - Login failed.')
            sys.exit(4)

    def download(self, packageName, versionCode=None, offerType=1):
        if self.authSubToken is None:
            Log.error('Google Play - You need to login before executing any request')
            sys.exit(4)

        if versionCode is None:
            appDetails = self.details(packageName).get('details').get('appDetails')
            versionCode = appDetails.get('versionCode')

        headers = self.getHeaders()
        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        response = requests.post(PURCHASE_URL, headers=headers,
                                 params=params,
                                 timeout=60)

        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            Log.error(f'Google Play - {response.commands.displayErrorMessage}')
            sys.exit(4)
        else:
            downloadToken = response.payload.buyResponse.downloadToken

        if downloadToken is not None:
            params['dtok'] = downloadToken
        response = requests.get(DELIVERY_URL, headers=headers, params=params, timeout=60)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            Log.error(f'Google Play - {response.commands.displayErrorMessage}')
            sys.exit(4)
        elif response.payload.deliveryResponse.appDeliveryData.downloadUrl == "":
            Log.error('Google Play - App not purchased')
            sys.exit(4)
        else:
            result = {'docId': packageName, 'additionalData': [], 'splits': []}
            downloadUrl = response.payload.deliveryResponse.appDeliveryData.downloadUrl
            cookie = response.payload.deliveryResponse.appDeliveryData.downloadAuthCookie[0]
            cookies = {
                str(cookie.name): str(cookie.value)
            }
            result['file'] = self._deliver_data(downloadUrl, cookies)

            for split in response.payload.deliveryResponse.appDeliveryData.split:
                a = {'name': split.name, 'file': self._deliver_data(split.downloadUrl, None)}
                result['splits'].append(a)
            return result, appDetails

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

    def details(self, packageName):
        path = DETAILS_URL + f'?doc={requests.utils.quote(packageName)}'
        data = self.executeRequestApi2(path)
        return utils.parseProtobufObj(data.payload.detailsResponse.docV2)

    def getHeaders(self, upload_fields=False):
        if upload_fields:
            headers = self.deviceBuilder.getDeviceUploadHeaders()
        else:
            headers = self.deviceBuilder.getBaseHeaders()
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = "GoogleLogin auth=%s" % self.authSubToken
        if self.device_config_token is not None:
            headers["X-DFE-Device-Config-Token"] = self.device_config_token
        if self.deviceCheckinConsistencyToken is not None:
            headers["X-DFE-Device-Checkin-Consistency-Token"] = self.deviceCheckinConsistencyToken
        if self.dfeCookie is not None:
            headers["X-DFE-Cookie"] = self.dfeCookie
        return headers

    def checkin(self, email, ac2dmToken):
        headers = self.getHeaders()
        headers["Content-Type"] = CONTENT_TYPE_PROTO

        request = self.deviceBuilder.getAndroidCheckinRequest()

        stringRequest = request.SerializeToString()
        res = self.session.post(CHECKIN_URL, data=stringRequest,
                                headers=headers, verify=ssl_verify)
        response = googleplay_pb2.AndroidCheckinResponse()
        response.ParseFromString(res.content)
        self.deviceCheckinConsistencyToken = response.deviceCheckinConsistencyToken

        request.id = response.androidId
        request.securityToken = response.securityToken
        request.accountCookie.append("[" + email + "]")
        request.accountCookie.append(ac2dmToken)
        stringRequest = request.SerializeToString()
        self.session.post(CHECKIN_URL,
                          data=stringRequest,
                          headers=headers,
                          verify=ssl_verify)

        return response.androidId

    def uploadDeviceConfig(self):
        upload = googleplay_pb2.UploadDeviceConfigRequest()
        upload.deviceConfiguration.CopyFrom(self.deviceBuilder.getDeviceConfig())
        headers = self.getHeaders(upload_fields=True)
        stringRequest = upload.SerializeToString()
        response = self.session.post(UPLOAD_URL, data=stringRequest,
                                     headers=headers,
                                     verify=ssl_verify,
                                     timeout=60)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        try:
            if response.payload.HasField('uploadDeviceConfigResponse'):
                self.device_config_token = response.payload.uploadDeviceConfigResponse
                self.device_config_token = self.device_config_token.uploadDeviceConfigToken
        except ValueError:
            pass

    def getAuthSubToken(self, email, passwd):
        requestParams = self.deviceBuilder.getLoginParams(email, passwd)
        requestParams['service'] = 'androidmarket'
        requestParams['app'] = 'com.android.vending'
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        with requests.Session() as s:
            s.headers = {'User-Agent': 'GoogleAuth/1.4', 'device': "{0:x}".format(self.gsfId)}
            response = s.post(AUTH_URL,
                              data=requestParams,
                              verify=ssl_verify)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "token" in params:
            master_token = params["token"]
            second_round_token = self.getSecondRoundToken(master_token, requestParams)
            self.authSubToken = second_round_token
        elif "error" in params:
            Log.error(f'Google Play - server says: " + {params["error"]}')
            sys.exit(4)
        else:
            Log.error('Google Play - auth token not found')
            sys.exit(4)

    def getSecondRoundToken(self, first_token, params):
        if self.gsfId is not None:
            params['androidId'] = "{0:x}".format(self.gsfId)
        params['Token'] = first_token
        params['check_email'] = '1'
        params['token_request_options'] = 'CAA4AQ=='
        params['system_partition'] = '1'
        params['_opt_is_called_from_account_manager'] = '1'
        params.pop('Email')
        params.pop('EncryptedPasswd')
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        response = self.session.post(AUTH_URL,
                                     data=params,
                                     headers=headers,
                                     verify=ssl_verify)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()

        if 'error' in params:
            raise ConnectionError('')

        if "auth" in params:
            return params["auth"]
        elif "error" in params:
            Log.error(f'Google Play - server says: " + {params["error"]}')
            sys.exit(4)
        else:
            Log.error('Google Play - auth token not found')
            sys.exit(4)

    def executeRequestApi2(self, path, post_data=None, content_type=CONTENT_TYPE_URLENC, params=None):
        if self.authSubToken is None:
            Log.error('You need to login before executing any request')
            sys.exit(4)
        headers = self.getHeaders()
        headers["Content-Type"] = content_type

        if post_data is not None:
            response = self.session.post(path,
                                         data=str(post_data),
                                         headers=headers,
                                         params=params,
                                         verify=ssl_verify,
                                         timeout=60)
        else:
            response = self.session.get(path,
                                        headers=headers,
                                        params=params,
                                        verify=ssl_verify,
                                        timeout=60)

        message = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if message.commands.displayErrorMessage != "":
            raise ConnectionError(message.commands.displayErrorMessage)

        return message

    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        response = self.session.get(url, headers=headers,
                                    cookies=cookies, verify=ssl_verify,
                                    stream=True, timeout=60)
        total_size = response.headers.get('content-length')
        chunk_size = 32 * (1 << 10)
        return {'data': response.iter_content(chunk_size=chunk_size),
                'total_size': total_size,
                'chunk_size': chunk_size}
