from Acquisition._Acquisition import aq_inner, aq_parent
from DateTime.DateTime import DateTime
from ftw.news import utils
from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NewsListingBlockView(BaseBlock):
    template = ViewPageTemplateFile('templates/news_listing_block.pt')

    @property
    def title(self):
        return self.context.portlet_title

    @property
    def rss_url(self):
        if self.context.show_rss_link:
            parent = aq_parent(aq_inner(self.context))
            return '/'.join([parent.absolute_url(), 'news_listing_rss'])
        return ''

    @property
    def more_news_url(self):
        if self.context.show_more_news_link:
            parent = aq_parent(aq_inner(self.context))
            return '/'.join([parent.absolute_url(), 'news_listing'])
        return ''

    def get_news(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        url_tool = getToolByName(self.context, 'portal_url')
        portal_path = url_tool.getPortalPath()
        query = {'object_provides': 'ftw.news.interfaces.INews'}

        if self.context.current_context:
            parent = aq_parent(aq_inner((self.context)))
            path = '/'.join(parent.getPhysicalPath())
            query['path'] = {'query': path}
        elif self.context.filter_by_path:
            cat_path = []
            for item in self.context.filter_by_path:
                cat_path.append('/'.join([portal_path, item]))
            query['path'] = {'query': cat_path}

        if self.context.subjects:
            query['Subject'] = self.context.subjects

        if self.context.maximum_age > 0:
            date = DateTime() - self.context.maximum_age
            query['effective'] = {'query': date, 'range': 'min'}

        query['sort_on'] = 'effective'
        query['sort_order'] = 'descending'
        brains = catalog.searchResults(query)

        if self.context.quantity:
            brains = brains[:self.context.quantity]

        return [self.get_item_dict(brain) for brain in brains]

    def get_item_dict(self, brain):
        obj = brain.getObject()

        description = ''
        if self.context.show_description:
            description = brain.Description
        if self.context.description_length:
            description = utils.crop_text(description,
                                          self.context.description_length)

        author = ''
        if utils.can_view_about():
            author = utils.get_creator(obj)

        item = {
            'title': brain.Title,
            'description': description,
            'url': brain.getPath(),
            'author': author,
            'effective_date': self.context.toLocalizedTime(brain.effective),
        }
        return item
