from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implements


class INewsSchema(model.Schema):
    """A folderish news type for blocks
    """


class News(Container):
    implements(INewsSchema)
