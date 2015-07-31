from ftw.news.interfaces import INewsFolder
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope.interface import alsoProvides
from zope.interface import implements


class INewsFolderSchema(form.Schema):
    pass

alsoProvides(INewsFolderSchema, IFormFieldProvider)


class NewsFolder(Container):
    implements(INewsFolder)
