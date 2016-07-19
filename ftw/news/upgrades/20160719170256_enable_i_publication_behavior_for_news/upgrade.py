from ftw.upgrade import UpgradeStep


class EnableIPublicationBehaviorForNews(UpgradeStep):
    """Enable IPublication behavior for news.
    """

    def __call__(self):
        self.install_upgrade_profile()
