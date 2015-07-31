from datetime import timedelta, datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
import transaction


def set_allow_anonymous_view_about(context, enable):
    site_props = getToolByName(
        context, 'portal_properties').site_properties
    site_props.allowAnonymousViewAbout = enable


class TestNewsListing(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsListing, self).setUp()
        self.grant('Manager')

        self.news_folder = create(Builder('news folder')
                                  .titled(u'A News Folder'))

        yesterday = datetime.today() - timedelta(days=1)
        self.news1 = create(Builder('news').titled(u'News Entry 1')
                            .within(self.news_folder)
                            .having(effective=yesterday, news_date=yesterday)
                            )

        tomorrow = datetime.today() + timedelta(days=1)
        self.news2 = create(Builder('news').titled(u'News Entry 2')
                            .within(self.news_folder)
                            .having(effective=tomorrow, news_date=tomorrow)
                            )

        set_allow_anonymous_view_about(self.news_folder, True)

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

    def _is_author_visible(self, browser):
        browser.login().visit(self.news_folder)
        return browser.css('span.documentAuthor')

    @browsing
    def test_member_sees_author_when_aava_disabled(self, browser):
        set_allow_anonymous_view_about(self.news_folder, False)
        browser.login(self.member).open(self.news_folder)
        self.assertTrue(self._is_author_visible(browser),
                        'Authenticated member should see author if '
                        'allowAnonymousViewAbout is False.')

    @browsing
    def test_member_sees_author_when_aava_enabled(self, browser):
        set_allow_anonymous_view_about(self.news_folder, True)
        browser.login(self.member).open(self.news_folder)
        self.assertTrue(self._is_author_visible(browser),
                        'Authenticated member should see author.')

    @browsing
    def test_anonymous_cannot_see_author_when_aava_disabled(self, browser):
        set_allow_anonymous_view_about(self.news_folder, False)
        browser.open(self.news_folder)
        self.assertTrue(self._is_author_visible(browser),
                        'Anonymous user should not see author if '
                        'allowAnonymousViewAbout is False.')

    @browsing
    def test_anonymous_sees_author_when_aava_enabled(self, browser):
        set_allow_anonymous_view_about(self.news_folder, True)
        browser.open(self.news_folder)
        self.assertTrue(self._is_author_visible(browser),
                        'Anonymous user should see author if '
                        'allowAnonymousViewAbout is True.')

    @browsing
    def test_inactive_news_is_visible_for_contributor(self, browser):
        browser.login(self.contributor).open(self.news_folder)
        self.assertEqual(2, len(browser.css('div.tileItem')))

    @browsing
    def test_inactive_news_is_not_visible_for_regular_users(self, browser):
        browser.login(self.member).open(self.news_folder)
        self.assertEqual(1, len(browser.css('div.tileItem')))

    @browsing
    def test_news_listing_inside_contentpage(self, browser):
        page = create(Builder('sl content page').titled(u'Content page'))
        news_folder = create(Builder(u'news folder')
                             .titled(u'A News Folder')
                             .within(page))

        browser.login().visit(page, view='@@news_listing')
        self.assertEquals('Content page - News', plone.first_heading())

        browser.visit(news_folder)
        self.assertEquals(u'A News Folder', plone.first_heading())

    @browsing
    def test_news_listing_title(self, browser):
        """
        This test makes sure that the news listing view renders the
        title of the portlet, not the generic title.
        """
        browser.login().visit(self.news_folder, view='news_listing')
        self.assertEquals(
            ['A News Folder'],
            browser.css('h1.documentFirstHeading').text
        )

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
        page_state = {
            "default": [
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": IUUID(block)
                                }
                            ]
                        }
                    ]
                },
            ]
        }
        page_config = IPageConfiguration(self.news1)
        page_config.store(page_state)
        transaction.commit()

        browser.login().visit(self.news_folder, view='news_listing')
        self.assertEqual(
            'Textblock with image',
            browser.css('.newsListing .tileBody img').first.attrib['title']
        )
