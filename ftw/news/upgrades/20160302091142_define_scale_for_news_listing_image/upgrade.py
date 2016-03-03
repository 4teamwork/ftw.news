from ftw.upgrade import UpgradeStep


class DefineScaleForNewsListingImage(UpgradeStep):
    """Define scale for news listing image.
    """

    def __call__(self):
        self.install_upgrade_profile()
