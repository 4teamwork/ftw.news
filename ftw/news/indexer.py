from ftw.news.contents.news import INewsSchema
from ftw.news.interfaces import INews
from plone.indexer import indexer


@indexer(INews)
def news_start_date(obj):
    return INewsSchema(obj).news_date
