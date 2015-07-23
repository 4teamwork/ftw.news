# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface


class INewsFolder(Interface):
    """Marker interface for the news folder"""


class INews(Interface):
    """Marker interface for the news item"""


class INewsListingView(Interface):
    """Marker interface for the news listing view"""


class INewsListingBlock(Interface):
    """Marker interface for the news listing blocks"""
