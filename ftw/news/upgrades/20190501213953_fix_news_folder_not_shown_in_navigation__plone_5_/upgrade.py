from ftw.news.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class FixNewsFolderNotShownInNavigationPlone5(UpgradeStep):
    """Fix news folder not shown in navigation (Plone 5).
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile()
