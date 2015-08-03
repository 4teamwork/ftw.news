from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.news.tests import utils
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestNewsListingBlockContentType(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListingBlockContentType, self).setUp()
        self.grant('Manager', 'Site Administrator')

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

        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block'))

        browser.login().visit(page)
        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')

    @browsing
    def test_news_listing_block_renders_rss_link(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block')
               .having(show_rss_link=True))

        browser.login().visit(page)
        self.assertEqual('Subscribe to the RSS feed',
                         browser.find('Subscribe to the RSS feed').text)

    @browsing
    def test_news_listing_block_has_no_rss_link(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        block = create(Builder('news listing block')
                       .within(page)
                       .titled('News listing block')
                       .having(show_rss_link=False))

        browser.login().visit(page)
        self.assertIsNone(browser.find('Subscribe to the RSS feed'))

        # Now edit the block so it will show the RSS link.
        browser.login().visit(block, view='edit')
        browser.fill({'Link to RSS feed': True}).save()

        browser.login().visit(page)
        self.assertEqual('Subscribe to the RSS feed',
                         browser.find('Subscribe to the RSS feed').text)

    @browsing
    def test_news_listing_block_shows_lead_image(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(page))
        news = create(Builder('news')
                      .titled(u'Hello World')
                      .within(news_folder)
                      .having(news_date=date(2000, 12, 31)))
        textblock = create(Builder('sl textblock')
                           .titled(u'Textblock with image')
                           .within(news)
                           .with_dummy_image())
        utils.create_page_state(news, textblock)

        block = create(Builder('news listing block')
                       .within(page)
                       .titled('News listing block')
                       .having(show_lead_image=True))

        lead_image_css_selector = '.newsListing .newsItem .image img'

        browser.login().visit(page)
        self.assertEqual(
            'Textblock with image',
            browser.css(lead_image_css_selector).first.attrib['title']
        )

        # Now edit the block so it will not show the lead image.
        browser.login().visit(block, view='edit')
        browser.fill({'Show lead image': False}).save()

        browser.login().visit(page)
        self.assertEqual([], browser.css(lead_image_css_selector))
