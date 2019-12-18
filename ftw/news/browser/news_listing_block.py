from Acquisition._Acquisition import aq_inner, aq_parent
from DateTime.DateTime import DateTime
from ftw.news import _
from ftw.news import utils
from ftw.news.behaviors.show_on_homepage.news import IShowOnHomepage
from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.utils import make_utf8
from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


class NewsListingBlockView(BaseBlock):
    template = ViewPageTemplateFile('templates/news_listing_block.pt')

    def get_block_info(self):
        """
        This method returns a dict containing information to be used in
        the block's template.
        """

        rss_link_url = ''
        if self.context.show_rss_link:
            rss_link_url = '/'.join([self.context.absolute_url(),
                                     'news_listing_rss'])

        more_news_link_url = ''
        if self.context.show_more_news_link:
            if self.context.link_to_more_items and self.context.link_to_more_items.to_object:
                more_news_link_url = self.context.link_to_more_items.to_object.absolute_url()
            else:
                more_news_link_url = '/'.join([self.context.absolute_url(), 'news_listing'])

        more_news_link_label = (
            self.context.more_news_link_label or
            translate(_('more_news_link_label', default=u'More News'),
                      context=self.request)
        )

        info = {
            'title': self.context.news_listing_config_title,
            'show_title': self.context.show_title,
            'more_news_link_url': more_news_link_url,
            'more_news_link_label': more_news_link_label,
            'rss_link_url': rss_link_url or '',
            'show_lead_image': self.context.show_lead_image,
            'hide_empty_block': self.context.hide_empty_block,
        }

        return info

    def get_news(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        brains = catalog.searchResults(
            **self.get_query()
        )

        if self.context.quantity:
            brains = brains[:self.context.quantity]

        return [self.get_item_dict(brain) for brain in brains]

    def get_query(self):
        query = {'object_provides': {
            'query': ['ftw.news.interfaces.INews'],
        }}
        parent = aq_parent(aq_inner((self.context)))

        if self.context.current_context:
            path = '/'.join(parent.getPhysicalPath())
            query['path'] = {'query': path}
        elif self.context.filter_by_path:
            cat_path = []
            for item in self.context.filter_by_path:
                if item.to_object:
                    cat_path.append('/'.join(item.to_object.getPhysicalPath()))
            query['path'] = {'query': cat_path}

        subjects = self.context.subjects
        if subjects:
            query['Subject'] = map(make_utf8, subjects)

        if self.context.maximum_age > 0:
            date = DateTime() - self.context.maximum_age
            query['start'] = {'query': date, 'range': 'min'}

        news_on_homepage = getattr(self.context, 'news_on_homepage', False)
        if news_on_homepage and IPloneSiteRoot.providedBy(parent):
            query['object_provides']['operator'] = 'and'
            query['object_provides']['query'].append(
                IShowOnHomepage.__identifier__
            )

        query['sort_on'] = 'start'
        query['sort_order'] = 'descending'

        # Show inactive news if the current user is allowed to add news items on the
        # parent of the news listing block. We must only render the inactive news
        # if the block renders news items from its parent (in order not to
        # allow the user to view news items he is not allowed to see).
        if self.context.current_context \
                and not self.context.filter_by_path \
                and api.user.has_permission('ftw.news: Add News', obj=parent):
            query['show_inactive'] = True

        return query

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

        image_tag = ''
        if INewsListingBaseSchema(self.context).show_lead_image:
            image_tag = obj.restrictedTraverse('@@leadimage')(
                'news_listing_image')

        show_review_state = self.context.show_review_state and \
            api.user.has_permission('ftw.news: Add News', obj=aq_parent(obj))
        review_state_title = self.get_translated_review_state_title_for(obj)

        item = {
            'title': brain.Title,
            'description': description,
            'url': brain.getURL(),
            'author': author,
            'news_date': self.format_date(brain),
            'image_tag': image_tag,
            'brain': brain,
            'review_state': {
                'show_review_state': show_review_state and review_state_title,
                'review_state_title': review_state_title,
                'review_state_id': brain.review_state,
            },
        }
        return item

    def format_date(self, brain):
        return self.context.toLocalizedTime(brain.start, long_format=False)

    def get_translated_review_state_title_for(self, obj):
        plone_utils = api.portal.get_tool('plone_utils')
        title = plone_utils.getReviewStateTitleFor(obj)
        if not title:
            return ''

        return translate(safe_unicode(title), domain='plone', context=self.request)
