import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze


class TestContentTypes(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestContentTypes, self).setUp()
        self.grant('Manager', 'Site Administrator')

    @browsing
    def test_add_news_folder(self, browser):
        browser.login().open()
        factoriesmenu.add('News Folder')

        news_folder_title = u'This is a news folder'
        browser.fill({'Title': news_folder_title}).save()

        statusmessages.assert_message(u'Item created')

    @browsing
    def test_news_folder_has_empty_listing_block(self, browser):
        self.grant('Manager')
        folder = create(Builder('news folder'))
        browser.login().visit(folder)
        self.assertEqual(
            ['No content available\n\nMore News'],
            browser.css('.sl-layout .ftw-news-newslistingblock').text
        )
        self.assertEqual(['news'], folder.objectIds())

    @browsing
    def test_add_news_item(self, browser):
        news_folder = create(Builder('news folder'))

        browser.login().visit(news_folder)
        factoriesmenu.add('News')

        news_item_title = u'This is a news entry'
        browser.fill({'Title': news_item_title}).save()
        self.assertEqual(news_item_title,
                         browser.css('h1.documentFirstHeading').first.text)

    @browsing
    def test_default_news_date(self, browser):
        news_folder = create(Builder('news folder'))

        with freeze(datetime.datetime(2001, 5, 7, 11, 13, 17)):
            news = create(Builder('news')
                          .titled(u'News Entry')
                          .within(news_folder))

        browser.login().open(news)
        self.assertEqual(
            'May 07, 2001',
            browser.css('.news-date').first.text
        )
