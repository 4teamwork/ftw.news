from ftw.news import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


class INewsOnHomepage(form.Schema):

    news_on_homepage = schema.Bool(
        title=_(u'news_listing_config_news_on_homepage_label',
                default=u'News on homepage'),
        description=_(
            u'news_listing_config_news_on_homepage_description',
            default=u'Only news items which have been marked to be '
                    u'shown on the homepage will be displayed.'),
        default=False,
        required=False,
    )
    form.order_after(news_on_homepage='current_context')

alsoProvides(INewsOnHomepage, IFormFieldProvider)
