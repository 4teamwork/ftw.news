from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestNewsDetail(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsDetail, self).setUp()
        self.grant('Manager')

    @browsing
    def test_news_detail_renders_date(self, browser):
        news_folder = create(Builder('news folder').titled(u'A News Folder'))

        news_date = datetime(2000, 12, 31, 13, 0, 0)
        news = create(Builder('news').titled(u'News Entry 1')
                      .within(news_folder)
                      .having(effective=news_date, news_date=news_date)
                      )

        browser.login().visit(news)
        self.assertEqual(
            'Dec 31, 2000',
            browser.css('p.newsDate').first.text
        )
