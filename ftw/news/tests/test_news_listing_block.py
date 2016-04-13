from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.news.tests import utils
from ftw.news.tests.utils import set_allow_anonymous_view_about
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import applyProfile


class TestNewsListingBlockContentType(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListingBlockContentType, self).setUp()
        self.grant('Manager', 'Site Administrator')

        self.member = create(Builder('user')
                             .named('John', 'Doe')
                             .with_roles('Member'))

    def _create_content_for_anonymous_view_about_tests(self):
        """
        This helper method creates some content which is used by multiple
        tests used to test if the author is shown or not depending on
        the value of "allowAnonymousViewAbout".
        """
        self.page = create(Builder('sl content page').titled(u'Content page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(self.page))
        create(Builder('news')
               .titled(u'Hello World')
               .within(news_folder)
               .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))
        create(Builder('news listing block')
               .within(self.page)
               .titled('News listing block'))

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
    def test_news_listing_block_renders_link_to_more_news(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block')
               .having(show_more_news_link=True))

        browser.login().visit(page)
        self.assertEqual('More News',
                         browser.find('More News').text)

    @browsing
    def test_news_listing_block_more_news_link_custom_label(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block')
               .having(show_more_news_link=True)
               .having(more_news_link_label=u'Really more news'))

        browser.login().visit(page)
        self.assertEqual('Really more news',
                         browser.find('Really more news').text)

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
        browser.visit(block, view='edit')
        browser.fill({'Link to RSS feed': True}).save()

        browser.visit(page)
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
                      .within(news_folder))
        textblock = create(Builder('sl textblock')
                           .titled(u'Textblock with image')
                           .within(news)
                           .with_dummy_image())
        utils.create_page_state(news, textblock)

        block = create(Builder('news listing block')
                       .within(page)
                       .titled('News listing block')
                       .having(show_lead_image=True))

        lead_image_css_selector = '.news-item img'

        browser.login().visit(page)
        self.assertEqual(
            'Textblock with image',
            browser.css(lead_image_css_selector).first.attrib['title']
        )

        # Now edit the block so it will not show the lead image.
        browser.visit(block, view='edit')
        browser.fill({'Show lead image': False}).save()

        browser.visit(page)
        self.assertEqual([], browser.css(lead_image_css_selector))

    @browsing
    def test_member_sees_author_when_aava_disabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(False)

        browser.login(self.member).open(self.page)
        self.assertEqual('Dec 31, 2000 03:00 PM by test_user_1_',
                         browser.css('.news-item .byline').first.text,
                         'Authenticated member should see author if '
                         'allowAnonymousViewAbout is False.')

    @browsing
    def test_member_sees_author_when_aava_enabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(True)

        browser.login(self.member).open(self.page)
        self.assertEqual('Dec 31, 2000 03:00 PM by test_user_1_',
                         browser.css('.news-item .byline').first.text,
                         'Authenticated member should see author.')

    @browsing
    def test_anonymous_cannot_see_author_when_aava_disabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(False)

        browser.logout().open(self.page)
        self.assertEqual('Dec 31, 2000 03:00 PM',
                         browser.css('.news-item .byline').first.text,
                         'Anonymous user should not see author if '
                         'allowAnonymousViewAbout is False.')

    @browsing
    def test_anonymous_sees_author_when_aava_enabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(True)

        browser.logout().open(self.page)
        self.assertEqual('Dec 31, 2000 03:00 PM by test_user_1_',
                         browser.css('.news-item .byline').first.text,
                         'Anonymous user should see author if '
                         'allowAnonymousViewAbout is True.')

    @browsing
    def test_has_image_class_is_set_on_show_lead_image(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(page))
        news_with_image = create(Builder('news')
                                 .titled(u'News with image')
                                 .within(news_folder))

        textblock_with_image = create(Builder('sl textblock')
                                      .titled(u'Textblock with image')
                                      .within(news_with_image)
                                      .with_dummy_image())

        utils.create_page_state(news_with_image, textblock_with_image)

        block = create(Builder('news listing block')
                       .within(page)
                       .titled('News listing block')
                       .having(show_lead_image=True))

        browser.login().visit(page)

        self.assertEqual(
            ['body show-image'],
            map(lambda news_item: news_item.attrib['class'],
                browser.css('.news-item .body'))
        )

    @browsing
    def test_has_image_class_is_not_set_on_show_lead_image(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(page))
        news_with_image = create(Builder('news')
                                 .titled(u'News with image')
                                 .within(news_folder))

        textblock_with_image = create(Builder('sl textblock')
                                      .titled(u'Textblock with image')
                                      .within(news_with_image)
                                      .with_dummy_image())

        utils.create_page_state(news_with_image, textblock_with_image)

        block = create(Builder('news listing block')
                       .within(page)
                       .titled('News listing block')
                       .having(show_lead_image=False))

        browser.login().visit(page)

        self.assertEqual(
            ['body'],
            map(lambda news_item: news_item.attrib['class'],
                browser.css('.news-item .body'))
        )

    @browsing
    def test_news_listing_block_on_homepage(self, browser):
        applyProfile(self.portal, 'ftw.news:show-on-homepage')

        newsfolder = create(Builder('news folder'))

        create(Builder('news')
               .within(newsfolder)
               .titled(u'News On Homepage')
               .having(show_on_homepage=True)
               .having(news_date=datetime(2011, 1, 2, 15, 0, 0)))

        create(Builder('news')
               .within(newsfolder)
               .having(show_on_homepage=False)
               .titled(u'News Not On Homepage')
               .having(news_date=datetime(2011, 1, 2, 15, 0, 0)))

        create(Builder('news listing block')
               .within(self.portal)
               .having(news_on_homepage=True))

        browser.login()
        browser.visit(self.portal, view='simplelayout-view')
        self.assertEqual(
            ['News On Homepage'],
            browser.css('.sl-block-content li.news-item .title').text,
            "The news listing block on the Plone Site must only render "
            "news items having been marked to be shown on the homepage."
        )
