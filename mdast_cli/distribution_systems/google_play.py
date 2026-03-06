import logging
from datetime import datetime
import asyncio

from mdast_cli.distribution_systems import google_play_apkeep as gp_apkeep
from mdast_cli.helpers.file_utils import ensure_download_dir

logger = logging.getLogger(__name__)


class GooglePlay(object):
    def __init__(self, email=None, aas_token=None):
        # New flow uses email + AAS token (or OAuth2->AAS upstream)
        self.email = email
        self.aas_token = aas_token

    def login(self):
        # No-op for apkeep-based flow; kept for backward compatibility
        logger.info('Google Play - Using apkeep-based integration (login is a no-op)')

    def get_gsf_id(self):
        # Not applicable in new flow
        return None

    def get_auth_subtoken(self):
        # Return provided token as-is (treated as AAS token)
        # Deprecated: kept for backward compatibility
        return self.aas_token

    def get_app_info(self, package_name):
        # Best-effort stub to keep interface; detailed app info not provided by apkeep CLI
        return {
            'integration_type': 'google_play',
            'package_name': package_name,
            'version_name': None,
            'version_code': None,
            'file_size': None,
            'icon_url': None
        }

    def download_app(self, download_path, package_name, file_name=None, proxy=None):
        # proxy is not used in the apkeep flow; preserved for signature compatibility
        ensure_download_dir(download_path)

        aas_token = self.aas_token or ''
        email = self.email or ''

        # Run async downloader synchronously
        artifact_path = asyncio.run(
            gp_apkeep.download_app(
                download_dir=download_path,
                package_name=package_name,
                email=email,
                aas_token=aas_token,
                timeout_sec=gp_apkeep.DEFAULT_TIMEOUT_SEC,
            )
        )

        return artifact_path

    @staticmethod
    def _get_upload_timestamp(info):
        try:
            upload_date = info.get('uploadDate')
            dt = datetime.strptime(upload_date, '%b %d, %Y')
        except Exception:
            now = datetime.now()
            dt = datetime(year=now.year, month=now.month, day=1)

        return int(dt.timestamp())
