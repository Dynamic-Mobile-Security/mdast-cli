"""Bounded subprocess bridge to the pinned ipatool SAP signer."""
import base64
import json
import logging
import platform
import queue
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)
AUTH_PATH = '/WebObjects/MZFinance.woa/wa/authenticate'
MAX_MESSAGE = 1 << 20
SETUP_TIMEOUT = 1800
SIGN_TIMEOUT = 120


class SAPError(Exception):
    pass


def validate_endpoint(value, authentication=False):
    try:
        url = urlsplit(value)
        host = (url.hostname or '').lower()
        valid = (url.scheme == 'https' and url.port in (None, 443)
                 and not url.username and not url.password and not url.fragment
                 and (host.endswith('.apple.com') or host == 's.mzstatic.com'))
        if authentication:
            valid = (valid and url.path == AUTH_PATH
                     and (host == 'buy.itunes.apple.com'
                          or host.endswith('-buy.itunes.apple.com')))
        if not valid:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise SAPError('Invalid Apple authentication/SAP endpoint') from None
    return value


def parse_bag(data):
    if not isinstance(data, dict):
        raise SAPError('Apple bag is not a dictionary')
    values = data.get('urlBag') or data.get('URLBag') or data
    if not isinstance(values, dict):
        raise SAPError('Apple bag has no SAP configuration')
    if str(values.get('sign-sap-version')) != '200':
        raise SAPError('Apple bag has missing or unsupported SAP version')
    return {
        'auth_url': validate_endpoint(values.get('authenticateAccount'), True),
        'setup_url': validate_endpoint(values.get('sign-sap-setup')),
        'certificate_url': validate_endpoint(values.get('sign-sap-setup-cert')),
        'version': 200,
    }


def helper_path():
    system = platform.system().lower()
    arch = {'x86_64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64',
            'amd64': 'amd64'}.get(platform.machine().lower())
    suffix = '.exe' if system == 'windows' else ''
    path = Path(__file__).with_name('bin') / f'mdast-sap-{system}-{arch}{suffix}'
    if arch is None or not path.is_file():
        raise SAPError('SAP helper is unavailable for this platform; install a complete mdast-cli release')
    return path


def helper_command():
    binary = helper_path()
    # Go/purego embeds the glibc interpreter in its Linux binary. On musl,
    # invoke the installed system loader explicitly; upstream selects the
    # corresponding checksum-pinned musllinux Unicorn runtime itself.
    if platform.system() == 'Linux':
        machine = {'amd64': 'x86_64', 'arm64': 'aarch64'}.get(
            platform.machine().lower(), platform.machine().lower())
        for directory in ('/lib', '/usr/lib'):
            loader = Path(directory) / ('ld-musl-' + machine + '.so.1')
            if loader.is_file():
                return [str(loader), str(binary)]
    return [str(binary)]


class SAPSigner:
    def __init__(self, config, guid):
        self.process = None
        try:
            hardware = bytes.fromhex(guid)
            if len(hardware) != 6:
                raise ValueError
        except (ValueError, TypeError):
            raise SAPError('SAP requires a 12-character hexadecimal GUID') from None
        try:
            self.process = subprocess.Popen(
                helper_command(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            logger.info('Preparing App Store SAP signer; first use downloads verified runtime assets')
            self._exchange({
                'op': 'init', 'version': config['version'], 'hardware_id': guid,
                'setup_url': config['setup_url'], 'certificate_url': config['certificate_url'],
            }, SETUP_TIMEOUT)
            logger.info('App Store SAP signer ready')
        except BaseException:
            self.close()
            raise

    def _exchange(self, message, timeout):
        data = json.dumps(message, separators=(',', ':')).encode() + b'\n'
        if len(data) > MAX_MESSAGE:
            raise SAPError('SAP request exceeds the size limit')
        result = queue.Queue(maxsize=1)

        process = self.process

        def communicate():
            try:
                process.stdin.write(data)
                process.stdin.flush()
                result.put(process.stdout.readline(MAX_MESSAGE + 1))
            except (OSError, ValueError):
                result.put(None)

        worker = threading.Thread(target=communicate, daemon=True)
        worker.start()
        try:
            raw = result.get(timeout=timeout)
            if not raw or len(raw) > MAX_MESSAGE or not raw.endswith(b'\n'):
                raise SAPError('SAP helper stopped or returned an invalid response')
            reply = json.loads(raw)
            if not isinstance(reply, dict) or reply.get('ok') is not True:
                # Upstream setup errors contain public asset/Apple URLs, but never
                # expose arbitrary helper output or authentication payloads here.
                raise SAPError('SAP helper failed during ' + message['op'])
            return reply
        except queue.Empty:
            self.close()
            raise SAPError('SAP helper timed out during ' + message['op']) from None
        except (ValueError, TypeError):
            self.close()
            raise SAPError('SAP helper returned malformed JSON') from None
        finally:
            if self.process is None or self.process.poll() is not None:
                worker.join(timeout=1)

    def sign(self, payload):
        reply = self._exchange({'op': 'sign', 'payload': base64.b64encode(payload).decode()}, SIGN_TIMEOUT)
        try:
            signature = base64.b64decode(reply['signature'], validate=True)
            if not signature or len(signature) > 65536:
                raise ValueError
            return base64.b64encode(signature).decode('ascii')
        except (KeyError, ValueError, TypeError):
            raise SAPError('SAP helper returned an invalid signature') from None

    def close(self):
        process = self.process
        if process is None:
            return
        # Terminate before closing pipes, which may still be blocked on setup.
        # No signer state is persisted; all native resources belong to this process.
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for pipe in (process.stdin, process.stdout):
            if pipe is not None:
                pipe.close()
        self.process = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
