from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestNewsListingBlockContentType(TestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListingBlockContentType, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Site Administrator'])

    @browsing
    def test_news_listing_block_can_be_added_on_contentpage(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))
        browser.login().visit(page)

        factoriesmenu.add('NewsListingBlock')
        browser.fill({
            'Title': u'This is a NewsListingBlock',
        }).save()

        browser.open(page)
        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')

    @browsing
    def test_news_listing_block_builder(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        block_builder = Builder('news listing block')
        block_builder.within(page)
        block_builder.titled('News')
        create(block_builder)

        browser.login().visit(page)
        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
