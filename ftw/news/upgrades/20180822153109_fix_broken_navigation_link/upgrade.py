from ftw.upgrade import UpgradeStep


class FixBrokenNavigationLink(UpgradeStep):
    """Fix broken navigation link.
    """

    def __call__(self):
        self.install_upgrade_profile()
