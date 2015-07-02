from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class NewsFolderBuilder(DexterityBuilder):
    portal_type = 'ftw.news.NewsFolder'

builder_registry.register('news folder', NewsFolderBuilder)
