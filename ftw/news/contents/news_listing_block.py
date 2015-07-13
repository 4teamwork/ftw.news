from ftw.news import _
from ftw.news.interfaces import INewsListingBlock
from ftw.news.portlets.news_portlet import INewsPortletSchema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class INewsListingBlockSchema(INewsPortletSchema):
    show_title = schema.Bool(
        title=_(u'news_listing_block_show_title_label', default=u'Show title'),
        default=True,
        required=False,
    )

    form.order_after(show_title='portlet_title')

alsoProvides(INewsListingBlockSchema, IFormFieldProvider)


class NewsListingBlock(Container):
    implements(INewsListingBlock)