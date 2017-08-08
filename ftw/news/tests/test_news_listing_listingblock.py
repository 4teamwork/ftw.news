import transaction
from DateTime import DateTime
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testing import freeze
from plone import api


class TestNewsListingOnNewsListingBlock(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListingOnNewsListingBlock, self).setUp()
        self.grant('Manager', 'Site Administrator')

        self.page = create(Builder('sl content page').titled(u'Content page'))

    def test_news_listing_optains_query_from_block(self):
        newslistingblock = create(Builder('news listing block')
                                  .within(self.page)
                                  .titled('News listing block'))

        news_listing_view = newslistingblock.restrictedTraverse('news_listing')
        block_view = newslistingblock.restrictedTraverse('block_view')

        self.assertDictEqual(news_listing_view.get_query(),
                             block_view.get_query())

    def test_news_listing_removes_start_date_from_query(self):
        newslistingblock = create(Builder('news listing block')
                                  .within(self.page)
                                  .having(maximum_age=5)
                                  .titled('News listing block'))

        news_listing_view = newslistingblock.restrictedTraverse('news_listing')
        block_view = newslistingblock.restrictedTraverse('block_view')

        self.assertNotIn('start', news_listing_view.get_query())
        self.assertIn('start', block_view.get_query())

    def test_news_listing_use_start_date_for_archive_portlet(self):
        newslistingblock = create(Builder('news listing block')
                                  .within(self.page)
                                  .titled('News listing block'))

        self.portal.REQUEST.set('archive', '2014/12/01')
        news_listing_view = newslistingblock.restrictedTraverse('news_listing')

        self.assertDictEqual({'query': (DateTime('2014/12/01').earliestTime(),
                                        DateTime('2014/12/31').latestTime()),
                              'range': 'minmax'},
                             news_listing_view.get_query()['start'])

    def test_query_newslisting_with_subject_containing_umlauts(self):
        newsfolder = create(Builder('news folder').within(self.page))
        news = create(Builder('news')
                      .within(newsfolder)
                      .titled(u'Some News')
                      .having(subjects=('F\xc3\xb6\xc3\xb6', 'Bar')))
        newslistingblock = create(Builder('news listing block')
                                  .within(self.page)
                                  .titled(u'News listing block')
                                  .having(subjects=(u'F\xf6\xf6', 'Bar')))

        view = newslistingblock.restrictedTraverse('block_view')
        self.assertTrue(len(view.get_news()), 'Expect one news item')
        self.assertEquals(news.Title(), view.get_news()[0]['title'])

    @browsing
    def test_block_renders_inactive_news_items(self, browser):
        news_folder = create(Builder('news folder'))

        with freeze(datetime(2010, 5, 17, 15, 34)):
            create(Builder('news')
                   .titled(u'Non-expired News Item')
                   .within(news_folder)
                   .having(news_date=datetime.now()))
            create(Builder('news')
                   .titled(u'Expired News Item')
                   .within(news_folder)
                   .having(news_date=datetime.now(),
                           expires=datetime.now() - timedelta(days=10)))

        news_listing_block = create(Builder('news listing block')
                                    .within(news_folder)
                                    .titled(u'News listing block'))

        james_bond = create(Builder('user')
                            .named('James', 'Bond')
                            .with_userid('james.bond'))

        # Make sure our user does not see the expired news item.
        browser.login(james_bond)
        browser.visit(news_listing_block, view='block_view')
        self.assertEqual(
            [
                'Non-expired News Item',
            ],
            browser.css('.news-item .title').text
        )

        # Now grant our user the permission to add news and make sure
        # he can see the expired news item.
        api.user.grant_roles(
            username=james_bond.getId(),
            roles=['Contributor'],
            obj=self.portal,
        )
        transaction.commit()
        browser.visit(news_listing_block, view='block_view')
        self.assertEqual(
            [
                'Non-expired News Item',
                'Expired News Item',
            ],
            browser.css('.news-item .title').text
        )
