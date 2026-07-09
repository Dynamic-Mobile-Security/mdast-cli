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

import requests

MODE_ENV_VAR = 'MDAST_CLI_MODE'
TLS_VERIFY_ENV_VAR = 'MDAST_TLS_VERIFY'
MODE_AUTO = 'auto'
MODE_MONOLITH = 'monolith'
MODE_MICROSERVICES = 'microservices'
PROBE_TIMEOUT = 20

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
    """GET a probe endpoint; return (status_code | None, parsed_json | None)."""
    try:
        resp = requests.get(f'{base_url}{path}',
                            headers={'Authorization': f'{scheme} {ci_token}'},
                            verify=verify,
                            timeout=PROBE_TIMEOUT)
    except requests.RequestException as ex:
        logger.debug(f'Probe {scheme} {path} failed: {type(ex).__name__}: {ex}')
        return None, None
    payload = None
    if resp.status_code == 200:
        try:
            payload = resp.json()
        except ValueError:
            payload = None
    return resp.status_code, payload


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

    # Microservices probe: Bearer + architectures, classify by payload shape.
    ms_status, ms_payload = _probe(base_url, '/architectures/', 'Bearer', ci_token, verify)
    if ms_status == 200 and _looks_microservices(ms_payload):
        logger.info('Detected microservices installation (Clark facade)')
        return MODE_MICROSERVICES

    # Monolith probe: Token + architectures, classify by payload shape.
    mono_status, mono_payload = _probe(base_url, '/architectures/', 'Token', ci_token, verify)
    if mono_status == 200 and _looks_monolith(mono_payload):
        logger.info('Detected monolith installation')
        return MODE_MONOLITH

    # Ambiguous 200 (payload matched neither shape) — do not guess.
    if ms_status == 200 or mono_status == 200:
        empty_list = ms_payload == [] or mono_payload == []
        hint = ('The /architectures/ list is empty, so the installation flavour cannot be '
                'inferred from it. ' if empty_list else
                'The payload matched neither the microservices (string type + os_version) '
                'nor the monolith (int type) shape. ')
        raise ModeDetectionError(
            f'Cannot detect installation mode: /architectures/ returned 200 but {hint}'
            f'Force the mode via {MODE_ENV_VAR}=monolith|microservices.')

    auth_error = 401 in (ms_status, mono_status) or 403 in (ms_status, mono_status)
    raise ModeDetectionError(
        'Cannot detect installation mode via GET /architectures/ '
        f'(Bearer -> {ms_status}, Token -> {mono_status}). '
        f'Check --url/--token, or force the mode via {MODE_ENV_VAR}.',
        auth_error=auth_error)
