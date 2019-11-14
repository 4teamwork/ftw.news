from DateTime import DateTime
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from ftw.news.tests import utils
from ftw.news.tests.utils import set_allow_anonymous_view_about
from ftw.news.utils import get_creator
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone


class TestNewsListing(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListing, self).setUp()
        self.grant('Manager')

        self.news_folder = create(Builder('news folder')
                                  .titled(u'A News Folder')
                                  .with_property('layout', 'news_listing'))

        yesterday = datetime.now() - timedelta(days=1)
        self.news1 = create(Builder('news')
                            .titled(u'News Entry 1')
                            .within(self.news_folder)
                            .having(news_date=yesterday))

        set_allow_anonymous_view_about(False)

        self.portal.manage_permission('Access inactive portal content',
                                      ['Contributor', 'Manager'],
                                      acquire=False)

        # Create user with local contributor role
        self.contributor = create(Builder('user')
                                  .named('Hugo', 'Boss')
                                  .with_roles('Contributor'))

        # Create user without special roles
        self.member = create(Builder('user')
                             .named('John', 'Doe')
                             .with_roles('Member'))

    @browsing
    def test_member_sees_author_when_aava_disabled(self, browser):
        set_allow_anonymous_view_about(False)
        browser.login(self.member)
        browser.visit(self.news_folder, view='@@news_listing')
        self.assertEqual(
            'by test_user_1_',
            browser.css('.news-item .news-author').first.text,
            'Authenticated member should see author if '
            'allowAnonymousViewAbout is False.')

    @browsing
    def test_member_sees_author_when_aava_enabled(self, browser):
        set_allow_anonymous_view_about(True)
        browser.login(self.member)
        browser.visit(self.news_folder, view='@@news_listing')
        self.assertEqual(
            'by test_user_1_',
            browser.css('.news-author').first.text,
            'Authenticated member should see author.')

    @browsing
    def test_anonymous_cannot_see_author_when_aava_disabled(self, browser):
        set_allow_anonymous_view_about(False)
        browser.logout().visit(self.news_folder, view='@@news_listing')
        self.assertEquals([], browser.css('.news-item .news-author'),
                          'Anonymous user should not see author if '
                          'allowAnonymousViewAbout is False.')

    @browsing
    def test_anonymous_sees_author_when_aava_enabled(self, browser):
        set_allow_anonymous_view_about(True)
        browser.logout().visit(self.news_folder, view='@@news_listing')
        self.assertEqual(
            'by test_user_1_',
            browser.css('.news-author').first.text,
            'Anonymous user should see author if '
            'allowAnonymousViewAbout is True.')

    @browsing
    def test_first_heading_of_news_listing_on_contentpage(self, browser):
        """
        This test makes sure that the first heading is correct when the
        view "@@news_listing" is called on a content page.
        "News" will be appended to the title of the content page.
        """
        page = create(Builder('sl content page')
                      .titled(u'Content page'))
        browser.login().visit(page, view='@@news_listing')
        self.assertEquals(u'Content page - News', plone.first_heading())

    @browsing
    def test_first_heading_of_news_listing_on_news_folder(self, browser):
        """
        This test makes sure that the first heading is correct when the
        view "@@news_listing" is called on a news folder.
        """
        news_folder = create(Builder(u'news folder')
                             .titled(u'A News Folder')
                             .with_property('layout', 'news_listing'))
        browser.visit(news_folder)
        self.assertEquals(u'A News Folder', plone.first_heading())

    @browsing
    def test_news_listing_no_description(self, browser):
        """
        This test makes sure that the news listing view does not
        render the generic description.
        """
        browser.login().visit(self.news_folder, view='news_listing')
        self.assertIsNone(
            plone.document_description(),
            'Found a document description which should not be there.'
        )

    @browsing
    def test_news_listing_lead_image(self, browser):
        """
        This test makes sure that the news listing view renders
        the lead image of a news entry.
        """
        block = create(Builder('sl textblock')
                       .titled(u'Textblock with image')
                       .within(self.news1)
                       .with_dummy_image())

        utils.create_page_state(self.news1, block)

        browser.login().visit(self.news_folder, view='news_listing')
        self.assertEqual(
            'Textblock with image',
            browser.css('.news-item img').first.attrib['title']
        )

    def test_get_creator_method_does_not_fail_if_user_is_inexistent(self):
        userid = 'inexisting'

        news = create(Builder('news')
                      .titled(u'News Entry 1')
                      .within(self.news_folder)
                      .having(news_date=datetime.now()))
        news.Creator = userid
        self.assertEquals(userid, get_creator(news))

    @browsing
    def test_contributor_can_see_inactive_news_in_news_listing_view(self, browser):
        container = create(Builder('news folder'))
        create(Builder('news')
               .titled(u'Future News')
               .within(container)
               .having(effective=datetime.now() + timedelta(days=10)))

        # Make sure an editor can see inactive news.
        contributor = create(Builder('user').named('A', 'Contributor').with_roles('Contributor'))
        browser.login(contributor).visit(container, view='news_listing')
        self.assertEquals(
            ['Future News'],
            browser.css('.news-listing .news-item .news-title').text
        )

        # Make sure an anonymous user does not see the inactive news.
        browser.logout().visit(container, view='news_listing')
        self.assertEquals(
            [],
            browser.css('.news-listing .news-item .news-title').text
        )


class TestNewsListingFormat(FunctionalTestCase):

    def setUp(self):
        super(TestNewsListingFormat, self).setUp()
        self.grant('Manager')

        self.news_folder = create(Builder('news folder')
                                  .with_property('layout', 'news_listing'))

    @browsing
    def test_show_full_creation_date_if_hour_and_minute_are_set(self, browser):
        create(Builder('news')
               .within(self.news_folder)
               .having(news_date=DateTime('2015/03/13 16:15')))

        browser.login().open(self.news_folder)
        self.assertEquals('Mar 13, 2015', browser.css('.news-date').first.text)

    @browsing
    def test_show_full_creation_date_if_minute_is_not_set(self, browser):
        create(Builder('news')
               .within(self.news_folder)
               .having(news_date=DateTime('2015/03/13 16:00')))

        browser.login().open(self.news_folder)

        self.assertEquals('Mar 13, 2015', browser.css('.news-date').first.text)

    @browsing
    def test_show_full_creation_date_if_hour_is_not_set(self, browser):
        create(Builder('news')
               .within(self.news_folder)
               .having(news_date=DateTime('2015/03/13 00:15')))

        browser.login().open(self.news_folder)

        self.assertEquals('Mar 13, 2015', browser.css('.news-date').first.text)

    @browsing
    def test_show_no_time_if_minute_and_hour_are_not_set(self, browser):
        create(Builder('news')
               .within(self.news_folder)
               .having(news_date=DateTime('2015/03/13 00:00')))

        browser.login().open(self.news_folder)

        self.assertEquals('Mar 13, 2015', browser.css('.news-date').first.text)
