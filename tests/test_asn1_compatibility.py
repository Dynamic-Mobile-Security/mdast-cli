"""Real RSA/Google signing paths with the updated ASN.1 dependency pair."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa
from google.auth import jwt
from google.auth.crypt import RSASigner
from google.oauth2 import service_account
from pyasn1.codec.der.decoder import decode
from pyasn1_modules import rfc8017
import rsa


def test_pkcs1_google_credentials_and_signed_assertion():
    key = crypto_rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption())
    parsed = rsa.PrivateKey.load_pkcs1(private_pem)
    encoded = parsed.save_pkcs1('DER')
    decoded, rest = decode(encoded, asn1Spec=rfc8017.RSAPrivateKey())
    assert not rest
    assert int(decoded['modulus']) == key.private_numbers().public_numbers.n
    signer = RSASigner.from_string(private_pem)
    credentials = service_account.Credentials(signer, 'service@example.test', 'https://example.test/token')
    assertion = credentials._make_authorization_grant_assertion()
    public_pem = key.public_key().public_bytes(serialization.Encoding.PEM,
                                             serialization.PublicFormat.SubjectPublicKeyInfo)
    payload = jwt.decode(assertion, certs=public_pem, audience='https://oauth2.googleapis.com/token')
    assert payload['iss'] == 'service@example.test'
