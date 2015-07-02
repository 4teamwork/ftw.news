from ftw.news import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class INewsFolderSchema(form.Schema):
    title = schema.TextLine(
        title=_(u'news_folder_title_label', default=u'Title'),
        required=False,
    )

    show_title = schema.Bool(
        title=_(u'news_folder_show_title_title_label', default=u'Show title'),
        default=True,
        required=False,
    )

alsoProvides(INewsFolderSchema, IFormFieldProvider)


class NewsFolder(Container):
    implements(INewsFolderSchema)
