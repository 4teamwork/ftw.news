from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from ftw.news import _
from ftw.news import utils
from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.interfaces import INewsListingView
from ftw.simplelayout.contenttypes.contents.interfaces import IContentPage
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implements


class NewsListing(BrowserView):
    implements(INewsListingView)

    def __init__(self, context, request):
        super(NewsListing, self).__init__(context, request)
        self.batch_size = 10

    @property
    def description(self):
        return self.context.Description()

    @property
    def batch(self):
        b_start = self.request.form.get('b_start', 0)
        return Batch(self.get_items(), self.batch_size, b_start)

    def get_query(self):
        query = {
            'object_provides': 'ftw.news.interfaces.INews',
            'sort_on': 'start',
            'sort_order': 'reverse',
            'path': '/'.join(self.context.getPhysicalPath())
        }

        datestring = self.request.get('archive')
        if datestring:
            try:
                start = DateTime(datestring)
            except DateTime.interfaces.SyntaxError:
                raise
            end = DateTime('{0}/{1}/{2}'.format(
                start.year() + start.month() / 12,
                start.month() % 12 + 1,
                1)
            ) - 1
            query['start'] = {
                'query': (start.earliestTime(), end.latestTime()),
                'range': 'minmax',
            }

        if api.user.has_permission('ftw.news: Add News', obj=self.context):
            query['show_inactive'] = True

        return query

    def get_items(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        show_inactive = _checkPermission(AccessInactivePortalContent,
                                         self.context)
        return catalog(self.get_query(), show_inactive=show_inactive)

    def get_item_dict(self, brain):
        obj = brain.getObject()

        news_listing_block = INewsListingBaseSchema(self.context, None)
        image_tag = ''
        if getattr(news_listing_block, 'show_lead_image', True):
            image_tag = obj.restrictedTraverse('@@leadimage')('news_listing_image', direction='thumbnail')

        item = {
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'author': utils.get_creator(obj) if utils.can_view_about() else '',
            'news_date': self.format_date(brain),
            'image_tag': image_tag,
            'has_image_class': image_tag and 'has-image' or 'no-image',
        }
        return item

    @property
    def title(self):
        title = self.context.Title()

        appendix = 'News'
        if IContentPage.providedBy(self.context) and title != appendix:
            return title + ' - ' + appendix

        return title

    @property
    def link(self):
        return self.context.absolute_url() + '/' + self.__name__

    def format_date(self, brain):
        return self.context.toLocalizedTime(brain.start, long_format=False)

    def get_rfc822(self, item):
        return DateTime(item.start).rfc822()


class NewsListingRss(NewsListing):

    max_items = 200

    def get_items(self):
        return super(NewsListingRss, self).get_items()[:self.max_items]

    @property
    def description(self):
        return _(u'label_feed_desc',
                 default=u'${title} - News Feed',
                 mapping={'title': safe_unicode(self.context.Title())})

    def get_channel_link_tag(self):
        """
        Returns a string containing a link tag.

        This is needed because TAL complains about empty HTML tags which
        cannot use "tal:content" when building the translation messages.
        """
        return '<link>{0}</link>'.format(self.context.absolute_url())

    def get_item_dict(self, brain):
        return {
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'news_date': brain.start.strftime(
                '%a, %e %b %Y %H:%M:%S %z'),
            'link_tag': '<link>{0}</link>'.format(brain.getURL())
        }


class NewsListingPortlet(NewsListing):

    def __init__(self, context, request):
        super(NewsListingPortlet, self).__init__(context, request)
        self.portlet = self.get_portlet()

    @property
    def description(self):
        return

    def get_portlet(self):
        manager_name = self.request.form.get('manager', None)
        name = self.request.form.get('portlet', None)
        if not manager_name or not name:
            return

        managers_and_assignments = self.get_manager_and_assignments(
            manager_name
        )
        for manager, assignments in managers_and_assignments:
            if name in assignments:
                return queryMultiAdapter(
                    (self.context, self.request, self,
                     manager, assignments[name]),
                    IPortletRenderer)

        return

    def get_manager_and_assignments(self, manager_name):
        context = self.context

        # Prepare a list of objects by walking up the path.
        contexts = [context]
        while not IPloneSiteRoot.providedBy(context):
            context = aq_parent(aq_inner(context))
            contexts.append(context)

        # Prepare a list of tuples in the form `(manager, assignments)`.
        managers_and_assignments = []
        for context in contexts:
            manager = getUtility(
                IPortletManager,
                name=manager_name,
                context=context)
            assignments = getMultiAdapter(
                (context, manager),
                IPortletAssignmentMapping,
                context=context)

            if assignments is not None:
                managers_and_assignments.append((manager, assignments))

        return managers_and_assignments

    def get_query(self):
        if self.portlet:
            portlet_query = self.portlet.get_query(all_news=True)
            view_query = super(NewsListingPortlet, self).get_query()

            if 'start' in view_query:
                portlet_query['start'] = view_query['start']
            return portlet_query

        # Fallback to default listing view behavior
        return super(NewsListingPortlet, self).get_query()

    def title(self):
        if self.portlet:
            return self.portlet.data.news_listing_config_title
        return super(NewsListingPortlet, self).title


class NewsListingOfNewsListingBlock(NewsListing):

    def get_query(self):
        block_view = self.context.restrictedTraverse('@@block_view')
        block_query = block_view.get_query()
        view_query = super(NewsListingOfNewsListingBlock, self).get_query()

        if 'start' in block_query:
            del block_query['start']

        if 'start' in view_query:
            block_query['start'] = view_query['start']

        return block_query


class NewsListingRssOfNewsListingBlock(NewsListingOfNewsListingBlock,
                                       NewsListingRss):
    @property
    def description(self):
        return _(u'label_feed_desc',
                 default=u'${title} - News Feed',
                 mapping={'title': safe_unicode(self.context.Title())})
