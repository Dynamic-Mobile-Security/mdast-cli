"""Installation mode resolution: monolith vs microservices (Clark facade).

The mode decides which backend the scan flow talks to, so it must be reliable in
BOTH directions (monolith -> monolith, k8s -> k8s). It is resolved as:

1. Explicit override via the ``MDAST_CLI_MODE`` env var
   (``monolith`` | ``microservices`` | ``auto``; default ``auto``). No new CLI
   flags are introduced (OOS-671-03).
2. Auto-detection by *content fingerprint*, not just an HTTP 200. Both
   installations expose ``GET {base}/architectures/`` under ``/rest``, but the
   payloads differ structurally:
     - microservices (scanyon-native): ``type`` is a string ``ANDROID``/``IOS``
       and each item carries ``os_version``;
     - monolith: ``type`` is an integer code (1/2) and there is no ``os_version``.
   Auth scheme also differs (microservices = ``Bearer``, monolith = ``Token``),
   so each probe uses its own scheme. A monolith that happens to answer 200 to a
   Bearer probe is NOT misclassified, because the payload is inspected.
"""
import logging
import os
from collections import namedtuple

import requests

MODE_ENV_VAR = 'MDAST_CLI_MODE'
TLS_VERIFY_ENV_VAR = 'MDAST_TLS_VERIFY'
MODE_AUTO = 'auto'
MODE_MONOLITH = 'monolith'
MODE_MICROSERVICES = 'microservices'
PROBE_TIMEOUT = 20

# Why a probe did not complete. Distinguished so the error message can point at
# the actual cause instead of blaming --url/--token for every transport failure.
FAILURE_TLS = 'tls'
FAILURE_PROXY = 'proxy'
FAILURE_NETWORK = 'network'

Probe = namedtuple('Probe', 'status payload failure detail')

logger = logging.getLogger(__name__)


class ModeDetectionError(Exception):
    """Raised when the installation flavour cannot be determined."""

    def __init__(self, message, auth_error=False):
        super().__init__(message)
        self.auth_error = auth_error


def tls_verify_enabled():
    """TLS verification is on unless explicitly disabled via env.

    Secure by default (the CLI carries an org-level bearer token): the operator
    must opt OUT with MDAST_TLS_VERIFY in {0,false,no,off} for self-signed stands.
    An unset OR empty value counts as "not configured" and stays secure, so a
    docker `-e MDAST_TLS_VERIFY` passthrough with no value can't silently
    disable verification.
    """
    raw = os.environ.get(TLS_VERIFY_ENV_VAR)
    if raw is None:
        return True
    raw = raw.strip().lower()
    if raw == '':
        return True
    return raw not in ('0', 'false', 'no', 'off')


def _looks_microservices(payload):
    """True if an /architectures/ payload is scanyon-native (microservices)."""
    if not isinstance(payload, list) or not payload:
        return False
    item = payload[0]
    if not isinstance(item, dict):
        return False
    # scanyon-native: type is a string ANDROID/IOS and os_version is present
    type_value = item.get('type')
    return isinstance(type_value, str) and type_value.upper() in ('ANDROID', 'IOS')


def _looks_monolith(payload):
    """True if an /architectures/ payload is monolith-shaped (int type code)."""
    if not isinstance(payload, list) or not payload:
        return False
    item = payload[0]
    return isinstance(item, dict) and isinstance(item.get('type'), int)


def _probe(base_url, path, scheme, ci_token, verify):
    """GET a probe endpoint.

    Returns a :class:`Probe`. ``failure`` is ``None`` when the request completed
    (whatever the status code) and one of the ``FAILURE_*`` constants when it did
    not, so the caller can tell a TLS problem from a dead proxy instead of
    reporting every transport error as a bad --url/--token.
    """
    try:
        resp = requests.get(f'{base_url}{path}',
                            headers={'Authorization': f'{scheme} {ci_token}'},
                            verify=verify,
                            timeout=PROBE_TIMEOUT)
    except requests.exceptions.SSLError as ex:
        logger.debug(f'Probe {scheme} {path} failed: SSLError: {ex}')
        return Probe(None, None, FAILURE_TLS, str(ex))
    except requests.exceptions.ProxyError as ex:
        logger.debug(f'Probe {scheme} {path} failed: ProxyError: {ex}')
        return Probe(None, None, FAILURE_PROXY, str(ex))
    except requests.RequestException as ex:
        logger.debug(f'Probe {scheme} {path} failed: {type(ex).__name__}: {ex}')
        return Probe(None, None, FAILURE_NETWORK, f'{type(ex).__name__}: {ex}')
    payload = None
    detail = None
    if resp.status_code == 200:
        try:
            payload = resp.json()
        except ValueError:
            payload = None
    elif resp.status_code in (401, 403):
        # The server explains itself ("Token has expired", ...) - keep the text so
        # the operator does not have to guess which half of the auth pair is wrong.
        detail = _body_snippet(resp, ci_token)
        logger.debug(f'Probe {scheme} {path} -> {resp.status_code}, body: {detail}')
    return Probe(resp.status_code, payload, None, detail)


def _body_snippet(resp, ci_token=None, limit=300):
    """Short single-line excerpt of a response body, for error messages.

    The token is redacted: this text is surfaced in exceptions and logs, and a
    server that echoes the credential back must not turn that into a leak.
    """
    try:
        text = resp.text or ''
    except Exception:  # pragma: no cover - defensive, .text should not raise
        return None
    text = ' '.join(text.split())
    if ci_token:
        text = text.replace(ci_token, '***')
    if not text:
        return None
    return text[:limit] + ('...' if len(text) > limit else '')


def _run_probes(base_url, ci_token, verify):
    """Probe both flavours once; return ``(mode | None, ms_probe, mono_probe)``."""
    # Microservices probe: Bearer + architectures, classify by payload shape.
    ms = _probe(base_url, '/architectures/', 'Bearer', ci_token, verify)
    if ms.status == 200 and _looks_microservices(ms.payload):
        return MODE_MICROSERVICES, ms, None

    # Monolith probe: Token + architectures, classify by payload shape.
    mono = _probe(base_url, '/architectures/', 'Token', ci_token, verify)
    if mono.status == 200 and _looks_monolith(mono.payload):
        return MODE_MONOLITH, ms, mono

    return None, ms, mono


def _failures(*probes):
    """Set of failure kinds seen across the given probes."""
    return {p.failure for p in probes if p is not None and p.failure}


def _diagnosis(ms, mono):
    """Actionable explanation for a failed detection, tailored to the cause.

    Every transport error used to surface as 'Check --url/--token', which sends
    the operator after a credential that is usually fine. Name the real cause.
    """
    failures = _failures(ms, mono)
    if FAILURE_TLS in failures:
        return ('The certificate could not be verified even with verification disabled, '
                'so the TLS handshake itself is failing. Check the proxy/TLS setup, or '
                f'force the mode via {MODE_ENV_VAR}=monolith|microservices.')
    if FAILURE_PROXY in failures:
        return ('The proxy is unreachable. Check HTTP_PROXY/HTTPS_PROXY/ALL_PROXY - they '
                'are often left set after a VPN is switched off; unset them to connect '
                'directly.')
    if FAILURE_NETWORK in failures:
        detail = (ms.detail if ms is not None and ms.failure else None) or \
                 (mono.detail if mono is not None and mono.failure else None)
        suffix = f' ({detail})' if detail else ''
        return f'The host could not be reached{suffix}. Check --url and network access.'

    # Both probes completed: this is a genuine HTTP-level answer, so quote it.
    details = [p.detail for p in (ms, mono) if p is not None and p.detail]
    if details:
        return f'Server said: {details[0]} - check --token (and --url).'
    return f'Check --url/--token, or force the mode via {MODE_ENV_VAR}.'


def resolve_installation_mode(base_url, ci_token, company_id, mode=None, verify=None):
    """Return MODE_MONOLITH or MODE_MICROSERVICES.

    ``base_url`` is the normalized base ending with ``/rest`` (both installations
    serve the CLI routes under this prefix).
    """
    if verify is None:
        verify = tls_verify_enabled()
    mode = (mode or os.environ.get(MODE_ENV_VAR) or MODE_AUTO).strip().lower()
    if mode == MODE_MONOLITH or mode == MODE_MICROSERVICES:
        logger.info(f'Installation mode forced via {MODE_ENV_VAR}: {mode}')
        return mode
    if mode != MODE_AUTO:
        raise ModeDetectionError(
            f'Unknown {MODE_ENV_VAR} value: {mode!r} '
            f'(expected {MODE_AUTO}/{MODE_MONOLITH}/{MODE_MICROSERVICES})')

    detected, ms, mono = _run_probes(base_url, ci_token, verify)
    if detected == MODE_MICROSERVICES:
        logger.info('Detected microservices installation (Clark facade)')
        return detected
    if detected == MODE_MONOLITH:
        logger.info('Detected monolith installation')
        return detected

    # TLS fallback: the monolith flow itself does not verify certificates, so a
    # certificate that only this probe rejects must not block the whole run -
    # that would fail at the door of a room with no walls (typical cause: a
    # corporate TLS-inspecting proxy re-signing with an internal CA).
    if verify and FAILURE_TLS in _failures(ms, mono):
        logger.warning(
            'TLS certificate verification failed while detecting the installation mode. '
            'Retrying the detection probe WITHOUT certificate verification. '
            f'This usually means a TLS-inspecting proxy is in the path - point '
            f'REQUESTS_CA_BUNDLE at your corporate root CA (in PEM; note that requests '
            f'uses the certifi bundle, NOT the OS trust store) to silence this.')
        insecure, ms_insecure, mono_insecure = _run_probes(base_url, ci_token, False)
        if insecure == MODE_MONOLITH:
            logger.info('Detected monolith installation (certificate not verified)')
            return MODE_MONOLITH
        if insecure == MODE_MICROSERVICES:
            # A microservices install DOES verify certificates for real traffic, so
            # resolving its mode over an unverified channel buys nothing - the scan
            # would fail moments later. Ask for an explicit decision instead.
            raise ModeDetectionError(
                'Detected a microservices installation, but only over a connection whose '
                'certificate could not be verified. Point REQUESTS_CA_BUNDLE at your '
                f'corporate root CA, or set {TLS_VERIFY_ENV_VAR}=0 to accept the risk '
                f'(the organization CI token would be sent over an unverified connection).')
        ms, mono = ms_insecure, mono_insecure

    # Ambiguous 200 (payload matched neither shape) — do not guess.
    if ms.status == 200 or mono.status == 200:
        empty_list = ms.payload == [] or mono.payload == []
        hint = ('The /architectures/ list is empty, so the installation flavour cannot be '
                'inferred from it. ' if empty_list else
                'The payload matched neither the microservices (string type + os_version) '
                'nor the monolith (int type) shape. ')
        raise ModeDetectionError(
            f'Cannot detect installation mode: /architectures/ returned 200 but {hint}'
            f'Force the mode via {MODE_ENV_VAR}=monolith|microservices.')

    auth_error = 401 in (ms.status, mono.status) or 403 in (ms.status, mono.status)
    raise ModeDetectionError(
        'Cannot detect installation mode via GET /architectures/ '
        f'(Bearer -> {ms.status}, Token -> {mono.status}). '
        f'{_diagnosis(ms, mono)}',
        auth_error=auth_error)
