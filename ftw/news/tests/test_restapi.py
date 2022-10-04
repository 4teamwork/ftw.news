from ftw.builder import Builder
from ftw.builder import create
from ftw.news.restapi.content import SerializeNewsListingBlockToJson
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from ftw.testbrowser import browsing


class TestRestApiIntegration(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestRestApiIntegration, self).setUp()
        self.grant('Manager', 'Site Administrator')

        self.layer['portal'].manage_permission(
            'plone.restapi: Use REST API',
            roles=['Anonymous']
        )

        self.newsfolder = create(Builder('news folder'))
        self.newslistingblock = self.newsfolder.objectValues()[0]
        self.news = create(Builder('news')
                           .within(self.newsfolder)
                           .titled(u'Some News'))

    def test_query_is_from_news_listing_block(self):
        self.assertDictEqual(
            self.newslistingblock.restrictedTraverse('@@news_listing').get_query(),
            SerializeNewsListingBlockToJson(self.newslistingblock, self.newslistingblock.REQUEST).get_query()
        )

    @browsing
    def test_do_not_serialize_news_by_default_on_block(self, browser):
        browser.open(self.newslistingblock.absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})
        self.assertNotIn('items', browser.json)

    @browsing
    def test_newslistingblock_has_block_configuration(self, browser):
        browser.open(self.newslistingblock.absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})
        self.assertIn('block-configuration', browser.json)

    @browsing
    def test_include_news(self, browser):
        browser.open(self.newslistingblock.absolute_url() + '?include_items=true', method='GET',
                     headers={'Accept': 'application/json'})
        self.assertIn('items', browser.json)

        news = browser.json['items'][0]
        self.assertEquals(self.news.Title().decode('utf-8'), news['title'])

    @browsing
    def test_pagination(self, browser):

        for number in range(0, 5):
            create(Builder('news')
                   .within(self.newsfolder)
                   .titled(u'News Nr. {}'.format(number)))
        browser.open(self.newslistingblock.absolute_url() + '?include_items=true&b_size=2', method='GET',
                     headers={'Accept': 'application/json'})

        self.assertEquals(6, browser.json['items_total'])
        self.assertIn('batching', browser.json)

    @browsing
    def test_serialize_news_by_default_on_newsfolder(self, browser):
        browser.open(self.newsfolder.absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})
        self.assertIn('items', browser.json)
