from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


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
        browser.find(news_folder_title).click()
        self.assertEqual(news_folder_title,
                         browser.css('h1.documentFirstHeading').first.text)

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

        now = datetime.now()
        news = create(Builder('news')
                      .titled(u'News Entry')
                      .within(news_folder))

        browser.login().open(news)
        self.assertIn(
            now.strftime('%b %d, %Y %I:'),
            browser.css('.newsDate').first.text
        )

