from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestNewsRssListing(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsRssListing, self).setUp()
        self.grant('Manager')

    def test_limit_search_results(self):
        news_folder = create(Builder('news folder'))
        create(Builder('news').titled(u'News Entry')
               .within(news_folder)
               .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))

        create(Builder('news').titled(u'News Entry')
               .within(news_folder)
               .having(news_date=datetime(2002, 12, 31, 15, 0, 0)))

        view = news_folder.unrestrictedTraverse('news_listing_rss')
        view.max_items = 200

        self.assertEqual(2, len(view.get_items()))

        view.max_items = 1

        self.assertEqual(1, len(view.get_items()))

    @browsing
    def test_channel_link(self, browser):
        news_folder = create(Builder('news folder'))

        browser.login().visit(news_folder, view='news_listing_rss')

        self.assertIn(
            '<link>{0}</link>'.format(news_folder.absolute_url()),
            browser.contents,
            'Did not found the link tag of the channel'
        )

    @browsing
    def test_news_listing_rss_items(self, browser):
        news_folder = create(Builder('news folder'))

        news = create(Builder('news').titled(u'News Entry')
                      .within(news_folder)
                      .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))

        browser.login().visit(news_folder, view='news_listing_rss')

        rdf = '<rdf:li rdf:resource="{0}"/>'.format(news.absolute_url())
        self.assertIn(rdf, browser.contents,
                      'Did not found the rdf tag for the news')

        link = '<link>{0}</link>'.format(news.absolute_url())
        self.assertIn(link, browser.contents,
                      'Did not found the link tag for the news')

    @browsing
    def test_news_item_contains_pubdate(self, browser):
        news_folder = create(Builder('news folder'))

        news = create(Builder('news').titled(u'News Entry')
                      .within(news_folder)
                      .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))

        browser.login().visit(news_folder, view='news_listing_rss')

        # Use HTML parser so that we have no XML namespaces.
        browser.parse_as_html()

        self.assertEqual(
            # Difference between "%e" and "%-e":
            # %e has a leading space on single numbers - that's why the tests
            # were failing between the 1st and the 9th every month :-)
            # %-e Removes the leading space - only works on unix machines.
            news.news_date.strftime('%a, %-e %b %Y %H:%M:%S %z').strip(),
            browser.css('rdf item pubDate').first.text
        )
