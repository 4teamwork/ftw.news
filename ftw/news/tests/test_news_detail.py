from datetime import datetime
from DateTime import DateTime
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
        news = create(Builder('news')
                      .titled(u'News Entry 1')
                      .within(news_folder)
                      .having(news_date=news_date))

        browser.login().visit(news)
        self.assertEqual(
            'Dec 31, 2000 01:00 PM',
            browser.css('.news-date').first.text
        )

class TestDateTimeFormat(FunctionalTestCase):

    def setUp(self):
        super(TestDateTimeFormat, self).setUp()
        self.grant('Manager')

        self.news_folder = create(Builder('news folder'))

    @browsing
    def test_show_full_creation_date_if_hour_and_minute_are_set(self, browser):
        news = create(Builder('news')
            .within(self.news_folder)
            .having(news_date=DateTime('2015/03/13 16:15')))

        browser.login().open(news)

        self.assertEquals('Mar 13, 2015 04:15 PM', browser.css('.news-date').first.text)

    @browsing
    def test_show_full_creation_date_if_minute_is_not_set(self, browser):
        news = create(Builder('news')
            .within(self.news_folder)
            .having(news_date=DateTime('2015/03/13 16:00')))

        browser.login().open(news)

        self.assertEquals('Mar 13, 2015 04:00 PM', browser.css('.news-date').first.text)

    @browsing
    def test_show_full_creation_date_if_hour_is_not_set(self, browser):
        news = create(Builder('news')
            .within(self.news_folder)
            .having(news_date=DateTime('2015/03/13 00:15')))

        browser.login().open(news)

        self.assertEquals('Mar 13, 2015 12:15 AM', browser.css('.news-date').first.text)

    @browsing
    def test_show_no_time_if_minute_and_hour_are_not_set(self, browser):
        news = create(Builder('news')
            .within(self.news_folder)
            .having(news_date=DateTime('2015/03/13 00:00')))

        browser.login().open(news)

        self.assertEquals('Mar 13, 2015', browser.css('.news-date').first.text)
