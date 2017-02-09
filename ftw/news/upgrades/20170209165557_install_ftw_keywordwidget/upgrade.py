from ftw.upgrade import UpgradeStep


class InstallFtwKeywordwidget(UpgradeStep):
    """Install "ftw.keywordwidget".
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.keywordwidget:default')
        self.install_upgrade_profile()
