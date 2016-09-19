from ftw.upgrade import UpgradeStep


class UseSimplelayoutForNewsFolders(UpgradeStep):
    """Use simplelayout for news folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
