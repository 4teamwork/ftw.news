from ftw.news import _
from ftw.news.interfaces import INewsFolder
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


class INewsFolderSchema(form.Schema):
    pass

alsoProvides(INewsFolderSchema, IFormFieldProvider)


class NewsFolder(Container):
    implements(INewsFolder)


def create_news_listing_block(news_folder, event=None):
    """
    This methods creates a news listing block inside the given news folder
    and is used as a handler for a subscriber listening to the creation
    of news folders.
    """

    title = translate(
        _(u'title_default_newslisting_block', u'News'),
        context=getSite().REQUEST
    )

    api.content.create(
        news_folder,
        'ftw.news.NewsListingBlock',
        title=title,
        news_listing_config_title=title,
        current_context=True,
        subjects=[],
        show_title=False,
        filter_by_path=[],
        show_more_news_link=True,
    )
