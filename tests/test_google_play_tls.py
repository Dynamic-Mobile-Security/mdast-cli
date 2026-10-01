"""The real bundled downloader must not send credentials to an untrusted peer."""
import asyncio
import datetime
import socket
import ssl
import threading

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mdast_cli.distribution_systems import google_play_apkeep as gp

pytestmark = pytest.mark.security


@pytest.mark.parametrize('operation', ['oauth', 'download'])
def test_bundled_apkeep_rejects_untrusted_tls(tmp_path, operation):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'android.clients.google.com')])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=1))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('android.clients.google.com')]), False)
            .sign(key, hashes.SHA256()))
    cert_path, key_path = tmp_path / 'cert.pem', tmp_path / 'key.pem'
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                         serialization.PrivateFormat.PKCS8,
                                         serialization.NoEncryption()))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    events, errors = [], []
    context.set_servername_callback(lambda sock, hostname, ctx: events.append(('sni', hostname)))
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen()
    listener.settimeout(10)
    proxy = f'http://127.0.0.1:{listener.getsockname()[1]}'

    def serve():
        try:
            conn, _ = listener.accept()
            with conn:
                conn.settimeout(8)
                request = b''
                while b'\r\n\r\n' not in request and len(request) < 16384:
                    chunk = conn.recv(1024)
                    if not chunk:
                        raise EOFError('Missing CONNECT request')
                    request += chunk
                events.append(('connect', request.split(b'\r\n', 1)[0]))
                conn.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                try:
                    with context.wrap_socket(conn, server_side=True) as tls:
                        events.append(('unexpected_http', tls.recv(4096)))
                except ssl.SSLError as error:
                    events.append(('tls_rejected', error.reason))
        except Exception as error:
            errors.append(type(error).__name__)
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        with pytest.raises(RuntimeError):
            if operation == 'oauth':
                asyncio.run(gp.fetch_aas_token('test@example.com', 'dummy-token', 8, proxy))
            else:
                asyncio.run(gp.download_app(str(tmp_path), 'com.example.app',
                                           'test@example.com', 'dummy-token', 8, proxy))
    finally:
        thread.join(11)
    assert not thread.is_alive()
    assert not errors
    assert ('connect', b'CONNECT android.clients.google.com:443 HTTP/1.1') in events
    assert ('sni', 'android.clients.google.com') in events
    assert any(kind == 'tls_rejected' and ('CERTIFICATE' in detail or 'UNKNOWN_CA' in detail)
               for kind, detail in events)
    assert not any(kind == 'unexpected_http' for kind, _ in events)
