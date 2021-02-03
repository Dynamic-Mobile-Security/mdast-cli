class DistributionSystem:
    """
    Base class for various distribution systems such HckeyApp, Firebase, AppsFlayer, etc
    """
    url = ''
    download_path = ''

    def __init__(self, app_identifier, app_version):
        self.app_identifier = app_identifier
        self.app_version = app_version

    def download_app(self):
        pass
