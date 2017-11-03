from Acquisition import aq_inner, aq_parent
from ftw.news import _
from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.interfaces import INewsListingBlock
from ftw.simplelayout.contenttypes.behaviors import IHiddenBlock
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from plone.uuid.interfaces import IUUID
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class INewsListingBlockSchema(INewsListingBaseSchema):
    show_title = schema.Bool(
        title=_(u'news_listing_block_show_title_label', default=u'Show title'),
        default=True,
        required=False,
    )

    more_news_link_label = schema.TextLine(
        title=_(u'label_more_news_link_label',
                default=u'Label for the "more news" link'),
        description=_(u'description_more_news_link_label',
                      default=u'This custom label will not be translated.'),
        required=False,
    )

    form.order_after(show_title='news_listing_config_title')
    form.order_after(more_news_link_label='show_more_news_link')

    hide_empty_block = schema.Bool(
        title=_(u'label_hide_empty_block',
                default=u'Hide empty block'),
        description=_(u'description_hide_empty_block',
                      default=u'Hide the block if there are no news items to be shown.'),
        default=False,
        required=False,
    )

alsoProvides(INewsListingBlockSchema, IFormFieldProvider)


class NewsListingBlock(Container):
    implements(INewsListingBlock, IHiddenBlock)

    def Title(self):
        return self.news_listing_config_title

    @property
    def is_hidden(self):
        if not self.hide_empty_block:
            return False

        # For unknown reason, `self` is not acquisition wrapped. We
        # need to get an acquisition wrapped news listing block we
        # work with.
        obj = api.content.get(UID=IUUID(self))

        if self.user_can_edit_block(obj):
            # Editors must always see the block or they cannot edit it anymore.
            return True

        items = api.content.get_view(
            name='block_view', context=obj, request=obj.REQUEST
        ).get_news()
        return self.hide_empty_block and not items

    @is_hidden.setter
    def is_hidden(self, value):
        """
        This is a dummy setter method in case somebody activates the IHiddenBlock
        behavior from ftw.simplelayout on the news listing block which makes no
        sense. It should not be a use case to allow hiding news listing blocks
        because the block does not really contain the objects, it only displays
        them from a different location. So if a news listing block ist not desired
        it should be removed from the content page instead.
        """
        raise Exception(
            'You are not allowed to add the IHiddenBlock behavior on the news listing block.'
        )

    def user_can_edit_block(self, obj):
        container = aq_parent(aq_inner(obj))
        return api.user.has_permission(
            'Modify portal content',
            obj=container,
        )
