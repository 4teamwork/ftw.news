from ftw.builder import builder_registry
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

    def titled(self, title):
        self.arguments['title'] = self.arguments['news_listing_config_title'] \
            = title
        return self


builder_registry.register('news listing block', NewsListingBlockBuilder)
