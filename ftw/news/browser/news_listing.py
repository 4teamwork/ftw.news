from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from DateTime.interfaces import SyntaxError as dtSytaxError
from ftw.news import _
from ftw.news.interfaces import INewsListingView
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView


class NewsListing(BrowserView):
    implements(INewsListingView)
    template = ViewPageTemplateFile('news_listing.pt')

    def __init__(self, context, request):
        super(NewsListing, self).__init__(context, request)
        self.batch = None

    def __call__(self):
        b_start = self.request.form.get('b_start', 0)
        self.batch = Batch(self.get_items(), 10, b_start)
        return self.template()

    def get_creator(self, item):
        memberid = item.Creator
        mt = getToolByName(self.context, 'portal_membership')
        member_info = mt.getMemberInfo(memberid)
        if member_info:
            fullname = member_info.get('fullname', '')
        else:
            fullname = None
        if fullname:
            return fullname
        else:
            return memberid

    def show_author(self):
        site_props = getToolByName(self.context,
                                   'portal_properties').site_properties
        membership_tool = getToolByName(self.context, 'portal_membership')

        allow_anonymous_view_about = site_props.getProperty(
            'allowAnonymousViewAbout', False)
        is_anonymous_user = membership_tool.isAnonymousUser()

        if not allow_anonymous_view_about and is_anonymous_user:
            return False
        return True

    def get_items(self):
        query = {
            'object_provides': 'ftw.news.interfaces.INews',
            'sort_on': 'effective',
            'sort_order': 'reverse'
        }
        show_inactive = _checkPermission(AccessInactivePortalContent,
                                         self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        # TODO: The following line makes RSS feed only work on news folders.
        query['path'] = '/'.join(self.context.getPhysicalPath())

        datestring = self.request.get('archive')
        if datestring:
            try:
                start = DateTime(datestring)
            except dtSytaxError:
                return query
            end = DateTime('%s/%s/%s' % (start.year() + start.month() / 12,
                                         start.month() % 12 + 1, 1))
            end = end - 1
            query['effective'] = {
                'query': (start.earliestTime(), end.latestTime()),
                'range': 'minmax',
            }

        return catalog(query, show_inactive=show_inactive)

    @property
    def title(self):
        title = self.context.Title()
        if self.context.portal_type == 'ftw.news.NewsFolder':
            return title
        return self.context.Title() + ' - News'

    @property
    def link(self):
        return self.context.absolute_url() + '/' + self.__name__

    @property
    def description(self):
        return _(u'label_feed_desc',
                 default=u'${title} - News Feed',
                 mapping={'title': self.context.Title().decode('utf-8')})


class NewsListingRss(NewsListing):
    template = ViewPageTemplateFile('news_listing_rss.pt')

    def get_channel_link_tag(self):
        """
        Returns a string containing a link tag.

        This is needed because TAL complains about empty HTML tags which
        cannot use "tal:content" when building the translation messages.
        """
        return '<link>{0}</link>'.format(self.link)

    def get_item_link_tag(self, url):
        """
        Returns a string containing a link tag.

        This is needed because TAL complains about empty HTML tags which
        cannot use "tal:content" when building the translation messages.
        """
        return '<link>{0}</link>'.format(url)


class NewsListingPortlet(NewsListing):

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

    def get_items(self):
        portlet = self.get_portlet()
        if portlet:
            return portlet.get_news(all_news=True)

        return []

    def title(self):
        portlet = self.get_portlet()
        if portlet:
            return portlet.data.portlet_title
        return super(NewsListingPortlet, self).title()
