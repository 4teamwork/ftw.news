from ftw.upgrade import UpgradeStep


class AddNewPermissionForTheMopageExternalUrl(UpgradeStep):
    """Add new permission for the mopage external url.
    """

    def __call__(self):
        self.install_upgrade_profile()
