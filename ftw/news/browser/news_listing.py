from DateTime import DateTime
from DateTime.interfaces import SyntaxError as dtSytaxError
from ftw.news import _
from ftw.news.interfaces import INewsListingView
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class NewsListing(BrowserView):
    implements(INewsListingView)
    template = ViewPageTemplateFile('news_listing.pt')

    def __init__(self, context, request):
        super(NewsListing, self).__init__(context, request)
        self.batch = None

    def __call__(self):
        b_start = self.request.form.get('b_start', 0)
        self.batch = Batch(self.get_items(), 10,
                           b_start)
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
        query['path'] = '/'.join(self.context.getPhysicalPath())
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
