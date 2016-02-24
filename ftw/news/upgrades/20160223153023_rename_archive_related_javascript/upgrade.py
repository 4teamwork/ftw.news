from ftw.upgrade import UpgradeStep


class RenameArchiveRelatedJavascript(UpgradeStep):
    """Rename archive related javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
