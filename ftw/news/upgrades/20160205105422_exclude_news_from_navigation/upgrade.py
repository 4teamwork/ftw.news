from ftw.upgrade import UpgradeStep


class ExcludeNewsFromNavigation(UpgradeStep):
    """Exclude news from navigation.
    """

    def __call__(self):
        self.install_upgrade_profile()
