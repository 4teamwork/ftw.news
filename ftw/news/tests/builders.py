from ftw.builder import builder_registry
from ftw.news.portlets import news_portlet
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
import transaction
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders


class NewsFolderBuilder(DexterityBuilder):
    portal_type = 'ftw.news.NewsFolder'

builder_registry.register('news folder', NewsFolderBuilder)


class NewsBuilder(DexterityBuilder):
    portal_type = 'ftw.news.News'

builder_registry.register('news', NewsBuilder)


class NewsListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.news.NewsListingBlock'

builder_registry.register('news listing block', NewsListingBlockBuilder)
