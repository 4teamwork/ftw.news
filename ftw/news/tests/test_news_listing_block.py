from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import utils
from ftw.news.tests.base import FunctionalTestCase
from ftw.news.tests.utils import set_allow_anonymous_view_about
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from plone import api
from plone.app.testing import applyProfile
from z3c.relationfield import create_relation
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid import IIntIds
import transaction


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
        browser.login().visit(block, view='news_listing')
        self.assertEqual(
            'Textblock with image',
            browser.css(lead_image_css_selector).first.attrib['title']
        )

        # Now edit the block so it will not show the lead image.
        browser.visit(block, view='edit')
        browser.fill({'Show lead image': False}).save()

        browser.visit(page)
        self.assertEqual([], browser.css(lead_image_css_selector))
        browser.login().visit(block, view='news_listing')
        self.assertEqual([], browser.css(lead_image_css_selector))

    @browsing
    def test_member_sees_author_when_aava_disabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(False)

        browser.login(self.member).open(self.page)
        self.assertEqual('Dec 31, 2000 by test_user_1_',
                         browser.css('.news-item .byline').first.text,
                         'Authenticated member should see author if '
                         'allowAnonymousViewAbout is False.')

    @browsing
    def test_member_sees_author_when_aava_enabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(True)

        browser.login(self.member).open(self.page)
        self.assertEqual('Dec 31, 2000 by test_user_1_',
                         browser.css('.news-item .byline').first.text,
                         'Authenticated member should see author.')

    @browsing
    def test_anonymous_cannot_see_author_when_aava_disabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(False)

        browser.logout().open(self.page)
        self.assertEqual('Dec 31, 2000',
                         browser.css('.news-item .byline').first.text,
                         'Anonymous user should not see author if '
                         'allowAnonymousViewAbout is False.')

    @browsing
    def test_anonymous_sees_author_when_aava_enabled(self, browser):
        self._create_content_for_anonymous_view_about_tests()

        set_allow_anonymous_view_about(True)

        browser.logout().open(self.page)
        self.assertEqual('Dec 31, 2000 by test_user_1_',
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

        create(Builder('news listing block')
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

        create(Builder('news listing block')
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
            browser.css('.sl-block-content .news-item .title').text,
            "The news listing block on the Plone Site must only render "
            "news items having been marked to be shown on the homepage."
        )

    @browsing
    def test_first_heading_of_news_listing_on_news_listing_block_within_root(self, browser):
        """
        This test makes sure that the first heading is correct when the
        view "@@news_listing" is called on a news listing block which has
        been added on the subsite view of the Plone site (root).
        """
        block = create(Builder('news listing block')
                       .titled(u'Awesome News'))

        browser.login().visit(block, view='@@news_listing')
        self.assertEquals(u'Awesome News', plone.first_heading())

    @browsing
    def test_first_heading_of_news_listing_on_news_listing_block_within_subsite(self, browser):
        """
        This test makes sure that the first heading is correct when the
        view "@@news_listing" is called on a news listing block which has
        been added on the subsite view of a subsite.
        """
        subsite = create(Builder('subsite').titled(u'My Subsite'))
        block = create(Builder('news listing block')
                       .titled(u'Awesome News')
                       .within(subsite))

        browser.login().visit(block, view='@@news_listing')
        self.assertEquals(u'Awesome News', plone.first_heading())

    @browsing
    def test_contributor_can_see_inactive_news_in_news_listing_block(self, browser):
        page = create(Builder('sl content page').titled(u'Content page'))
        create(Builder('news listing block')
               .within(page)
               .titled('News listing block'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(page))
        create(Builder('news')
               .titled(u'Future News')
               .within(news_folder)
               .having(effective=datetime.now() + timedelta(days=10)))

        # Make sure a contributor can see inactive news.
        contributor = create(Builder('user').named('A', 'Contributor').with_roles('Contributor'))
        browser.login(contributor).visit(page)
        self.assertEquals(
            ['Future News'],
            browser.css('.sl-block.ftw-news-newslistingblock .news-item .title').text
        )

        # Make sure an anonymous user does not see the inactive news.
        browser.logout().visit(page)
        self.assertEquals(
            [],
            browser.css('.sl-block.ftw-news-newslistingblock .news-item .title').text
        )

    @browsing
    def test_news_listing_block_filters_by_path(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        block = create(Builder('news listing block')
                       .titled(u'Awesome News'))

        news_folder_1 = create(Builder('news folder')
                               .titled(u'News Folder 1')
                               .within(page))
        create(Builder('news')
               .titled(u'A News Item in News Folder 1')
               .within(news_folder_1))

        news_folder_2 = create(Builder('news folder')
                               .titled(u'News Folder 2')
                               .within(page))
        create(Builder('news')
               .titled(u'A News Item in News Folder 2')
               .within(news_folder_2))

        browser.login()

        # By default, the block renders news from the children of
        # its container.
        browser.visit(block.absolute_url() + '/block_view')
        self.assertItemsEqual(
            [
                'A News Item in News Folder 1',
                'A News Item in News Folder 2',
            ],
            browser.css('.news-item .title').text
        )

        # Tell the block to only render news from a certain news folder
        block.current_context = False
        block.filter_by_path = [
            create_relation('/'.join(news_folder_1.getPhysicalPath())),
        ]
        transaction.commit()

        browser.reload()
        self.assertEqual(
            [
                'A News Item in News Folder 1',
            ],
            browser.css('.news-item .title').text
        )



    @browsing
    def test_block_without_news_can_be_marked_as_hidden(self, browser):
        """
        This test makes sure that there is a CSS class "hidden" on the block
        if the block is empty and the block has been configured accordingly.
        """
        page = create(Builder('sl content page'))
        block = create(Builder('news listing block')
                       .within(page)
                       .titled(u'News listing block'))

        def _block_has_hidden_class(browser):
            return 'hidden' in browser.css('.ftw-news-newslistingblock').first.attrib['class']

        browser.login()

        # Make sure the block has no "hidden" class.
        browser.visit(page)
        self.assertFalse(_block_has_hidden_class(browser))

        # Edit the block.
        browser.visit(block, view='edit')
        browser.fill({u'Hide empty block': True}).find('Save').click()

        # Make sure the block has a "hidden" class now.
        browser.visit(page)
        self.assertTrue(_block_has_hidden_class(browser))

    @browsing
    def test_hidden_empty_block_can_be_seen_by_admin(self, browser):
        page = create(Builder('sl content page'))
        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block')
               .having(hide_empty_block=True))

        # Authorized users can see the empty news listing block.
        browser.login()
        browser.visit(page)
        self.assertEqual(
            [
                'No content available',
                'The block is only visible to editors so it can still be edited.'
            ],
            browser.css('.ftw-news-newslistingblock p').text
        )

        # Anonymous users do not see the empty news listing block.
        browser.logout()
        browser.visit(page)
        self.assertEqual(
            [],
            browser.css('.ftw-news-newslistingblock').text
        )

    @browsing
    def test_custom_link_to_show_more_news(self, browser):

        page = create(Builder('sl content page')
                      .titled(u'Content Page'))

        page_to_link = create(Builder('sl content page')
                              .titled(u'Content Page'))

        news_folder = create(Builder('news folder').
                             titled(u'news Folder')
                             .within(page))
        create(Builder('news')
               .titled(u'News')
               .within(news_folder))
        block = create(Builder('news listing block')
                       .within(page)
                       .having(show_more_news_link=True)
                       .titled(u'This is a NewsListingBlock'))

        browser.login().visit(page)
        self.assertEqual(
            'http://nohost/plone/content-page/ftw-news-newslistingblock/news_listing',
            browser.find('More News').attrib['href']
        )

        browser.login().visit(block, view='@@edit')
        browser.fill({'Link to more items': page_to_link}).submit()
        browser.login().visit(page)

        self.assertEqual(
            page_to_link.absolute_url(),
            browser.find('More News').attrib['href']
        )

    @browsing
    def test_custom_link_to_show_more_items_when_target_is_deleted(self, browser):

        page = create(Builder('sl content page').titled(u'A page'))

        target = create(Builder('sl content page')
                        .titled(u'Target of the link to more items'))

        create(Builder('news listing block')
               .within(page)
               .having(show_more_news_link=True)
               .having(link_to_more_items=RelationValue(getUtility(IIntIds).getId(target)))
               .titled(u'This is a NewsListingBlock'))

        browser.login().visit(page)
        self.assertEqual(
            'http://nohost/plone/target-of-the-link-to-more-items',
            browser.find('More News').attrib['href']
        )

        self.portal.manage_delObjects(ids=[target.getId()])
        transaction.commit()

        browser.login().visit(page)

        self.assertEqual(
            'http://nohost/plone/a-page/ftw-news-newslistingblock/news_listing',
            browser.find('More News').attrib['href']
        )

    @browsing
    def test_show_review_state_for_news_items(self, browser):
        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.setDefaultChain('one_state_workflow')

        page = create(Builder('sl content page'))
        news_folder = create(Builder('news folder').within(page))
        create(Builder('news')
               .within(news_folder)
               .having(news_date=datetime(2000, 12, 31, 15, 0, 0))
               .titled(u'A news'))

        create(Builder('news listing block')
               .within(page)
               .titled(u'News listing block')
               .having(show_review_state=True))

        # With permission
        browser.login().visit(page)
        self.assertEqual('Dec 31, 2000 by test_user_1_ Published',
                         browser.css('.news-item .byline').first.text)

        # Without permission
        self.grant()
        browser.login().visit(page)
        self.assertEqual('Dec 31, 2000 by test_user_1_',
                         browser.css('.news-item .byline').first.text)
