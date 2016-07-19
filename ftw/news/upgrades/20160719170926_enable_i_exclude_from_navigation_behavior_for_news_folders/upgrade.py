from ftw.upgrade import UpgradeStep


class EnableIExcludeFromNavigationBehaviorForNewsFolders(UpgradeStep):
    """Enable IExcludeFromNavigation behavior for news folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
