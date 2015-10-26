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

    # Because a newsfolder will have a lot of content,
    # we use an unordered container to increase the
    # performace.
    _ordering = u'unordered'
