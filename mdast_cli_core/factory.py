"""Installation mode resolution (monolith vs microservices) and client factory.

No new CLI flags are introduced (OOS-671-03): the mode comes from the
MDAST_CLI_MODE environment variable (`auto` | `monolith` | `microservices`,
default `auto`) or is detected by probing.

Auto-detection probe: `GET {base}/engines/` exists only on the Clark facade
(the monolith serves engines under `/organizations/{id}/engines/`), so a 200
identifies the microservices installation; otherwise the monolith path is
probed with the legacy `Token` auth scheme.
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
    """Raised when neither installation flavour answered the probes."""

    def __init__(self, message, auth_error=False):
        super().__init__(message)
        self.auth_error = auth_error


def tls_verify_enabled():
    return os.environ.get(TLS_VERIFY_ENV_VAR, '').strip().lower() in ('1', 'true', 'yes', 'on')


def resolve_installation_mode(base_url, ci_token, company_id, mode=None, verify=None):
    """Return MODE_MONOLITH or MODE_MICROSERVICES.

    `base_url` is the normalized base ending with `/rest` (both installations
    serve the CLI routes under this prefix).
    """
    if verify is None:
        verify = tls_verify_enabled()
    mode = (mode or os.environ.get(MODE_ENV_VAR) or MODE_AUTO).strip().lower()
    if mode in (MODE_MONOLITH, MODE_MICROSERVICES):
        logger.info(f'Installation mode forced via {MODE_ENV_VAR}: {mode}')
        return mode
    if mode != MODE_AUTO:
        raise ModeDetectionError(
            f'Unknown {MODE_ENV_VAR} value: {mode!r} '
            f'(expected {MODE_AUTO}/{MODE_MONOLITH}/{MODE_MICROSERVICES})')

    ms_status = None
    try:
        resp = requests.get(f'{base_url}/engines/',
                            headers={'Authorization': f'Bearer {ci_token}'},
                            verify=verify,
                            timeout=PROBE_TIMEOUT)
        ms_status = resp.status_code
        if resp.status_code == 200:
            logger.info('Detected microservices installation (Clark facade)')
            return MODE_MICROSERVICES
    except requests.RequestException as ex:
        logger.debug(f'Microservices probe failed: {ex}')

    monolith_status = None
    try:
        resp = requests.get(f'{base_url}/organizations/{company_id}/engines/',
                            headers={'Authorization': f'Token {ci_token}'},
                            verify=verify,
                            timeout=PROBE_TIMEOUT)
        monolith_status = resp.status_code
        if resp.status_code == 200:
            logger.info('Detected monolith installation')
            return MODE_MONOLITH
    except requests.RequestException as ex:
        logger.debug(f'Monolith probe failed: {ex}')

    auth_error = 401 in (ms_status, monolith_status) or 403 in (ms_status, monolith_status)
    raise ModeDetectionError(
        'Cannot detect installation mode: probes failed '
        f'(microservices GET /engines/ -> {ms_status}, '
        f'monolith GET /organizations/{{id}}/engines/ -> {monolith_status}). '
        f'Check --url and --token, or force the mode via {MODE_ENV_VAR}.',
        auth_error=auth_error)
