from ftw.news import _
from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.interfaces import INewsListingBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
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

alsoProvides(INewsListingBlockSchema, IFormFieldProvider)


class NewsListingBlock(Container):
    implements(INewsListingBlock)
