from ftw.upgrade import UpgradeStep


class InstallBrowserLayerForFtwNews(UpgradeStep):
    """Install browser layer for "ftw.news".
    """

    def __call__(self):
        self.install_upgrade_profile()
