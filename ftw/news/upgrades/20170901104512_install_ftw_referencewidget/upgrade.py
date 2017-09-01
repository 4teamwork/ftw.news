from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.portlets.news_portlet import Assignment
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.upgrade import UpgradeStep
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from z3c.relationfield import create_relation
from z3c.relationfield.interfaces import IRelationValue
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility


class InstallFtwReferencewidget(UpgradeStep):
    """Install "ftw.referencewidget".
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.referencewidget:default')
        self.install_upgrade_profile()
        self.migrate_news_listing_blocks()
        self.migrate_news_portlets()

    def _convert_filter_by_path(self, filter_by_path):
        """
        `filter_by_path` is either a list of strings (paths) or a list
        of relation values.
        """
        new_filter_list = []
        for item in filter_by_path:
            if not IRelationValue.providedBy(item):
                # On the first run of the upgrade step, "item" is a string
                # because of the `PathSourceBinder` used until now.
                relation = self._create_relation_from_path(item)
            else:
                # On subsequent runs of the upgrade step, `item` is a relation
                # value because it already has been converted.
                relation = item
            new_filter_list.append(relation)
        return new_filter_list

    def _create_relation_from_path(self, path):
        """
        `path` is a string indicating the path to an object (without
        the path to the Plone Site).
        """
        path = '/'.join(self.portal.getPhysicalPath()) + path
        obj = self.portal.unrestrictedTraverse(path, None)
        if not obj:
            # The obj does not exist anymore.
            return None
        return create_relation('/'.join(obj.getPhysicalPath()))

    def migrate_news_listing_blocks(self):
        objs = self.objects(
            catalog_query={'portal_type': 'ftw.news.NewsListingBlock'},
            message='Convert news listing block to ftw.referencewidget'
        )
        for obj in objs:
            schema = INewsListingBaseSchema(obj, None)
            if schema and schema.filter_by_path:
                obj.filter_by_path = self._convert_filter_by_path(schema.filter_by_path)
                obj._p_changed = True

    def migrate_news_portlets(self):
        objs = self.objects(
            {'object_provides': ISimplelayout.__identifier__},
            'Convert news portlets to ftw.referencewidget'
        )
        for obj in objs:
            self.migrate_news_portlet(obj)

    def migrate_news_portlet(self, obj):
        annotations = IAnnotations(obj, None)
        if not annotations:
            return

        managers = tuple(annotations.get('plone.portlets.contextassignments', []))

        for manager_name in managers:
            manager = getUtility(IPortletManager, name=manager_name, context=obj)
            assignments = getMultiAdapter(
                (obj, manager),
                IPortletAssignmentMapping,
                context=obj
            )

            for portlet_name in assignments:
                portlet = assignments[portlet_name]
                if isinstance(portlet, Assignment):
                    filter_by_path = getattr(portlet.data, 'filter_by_path', [])
                    if not filter_by_path:
                        continue
                    portlet.data.filter_by_path = self._convert_filter_by_path(filter_by_path)
