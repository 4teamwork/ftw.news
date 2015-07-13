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

        self.news_folder = create(Builder('news folder')
                                  .titled(u'A News Folder'))

        self.news = create(Builder('news').titled(u'News Entry')
                           .within(self.news_folder))

    @browsing
    def test_news_listing_rss_items(self, browser):
        browser.login().visit(self.news_folder, view='news_listing_rss')

        rdf = '<rdf:li rdf:resource="{0}"/>'.format(self.news.absolute_url())
        self.assertIn(rdf, browser.contents,
                      'Did not found the rdf tag for the news')

        link = '<link>{0}</link>'.format(self.news.absolute_url())
        self.assertIn(link, browser.contents,
                      'Did not found the link tag for the news')

    @browsing
    def test_news_item_contains_pubdate(self, browser):
        browser.login().visit(self.news_folder, view='news_listing_rss')

        # Use HTML parser so that we have no XML namespaces.
        browser.parse_as_html()

        effective_date = self.news.effective()
        self.assertEqual(
            # Difference between "%e" and "%-e":
            # %e has a leading space on single numbers - that's why the tests
            # were failing between the 1st and the 9th every month :-)
            # %-e Removes the leading space - only works on unix machines.
            effective_date.strftime('%a, %-e %b %Y %H:%M:%S %z').strip(),
            browser.css('rdf item pubDate').first.text
        )
