from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestNewsPortletListing(TestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.portal_url = self.portal.portal_url()

    def test_no_portlet_found(self):
        self.request.form.update({'portlet': 'not_existing'})
        view = self.portal.unrestrictedTraverse('news_portlet_listing')
        self.assertEqual(None, view.get_portlet())

    def test_portlet_found_in_left_column(self):
        portlet = create(Builder('news portlet'))
        self.request.form.update({'portlet': portlet.__name__,
                                  'manager': u'plone.leftcolumn'})
        view = self.portal.unrestrictedTraverse('news_portlet_listing')
        self.assertEqual(portlet,
                         view.get_portlet().data)

    @browsing
    def test_left_column_portlet(self, browser):
        folder = create(Builder('news folder').titled(u'News'))
        create(Builder('news').titled(u'Bookings open').within(folder))

        create(Builder('news portlet')
               .having(current_context=False,
                       path=['/{0}'.format(folder.getId())],
                       show_more_news_link=True))

        browser.login().open()
        browser.find('More News').click()
        self.assertEquals(['Bookings open'],
                          browser.css('h2.tileHeadline').text)

    @browsing
    def test_right_column_portlet(self, browser):
        folder = create(Builder('news folder').titled(u'News'))
        create(Builder('news').titled(u'Bookings open').within(folder))

        create(Builder('news portlet')
               .in_manager(u'plone.rightcolumn')
               .having(current_context=False,
                       path=['/{0}'.format(folder.getId())],
                       show_more_news_link=True))

        browser.login().open()
        browser.find('More News').click()
        self.assertEquals(['Bookings open'],
                          browser.css('h2.tileHeadline').text)

    @browsing
    def test_news_listing_of_inherited_news_portlet(self, browser):
        # Create a news portlet on root which will be inherited by the root's
        # child objects.
        create(Builder('news portlet')
               .in_manager(u'plone.rightcolumn')
               .within(self.portal)
               .having(portlet_title=u'Aktuell',
                       show_more_news_link=True,
                       quantity=5,
                       maximum_age=10))

        # Create a content page having a news folder. Create an old news
        # entry in the news folder.
        content_page = create(Builder('sl content page')
                              .titled(u'My Content Page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News')
                             .within(content_page))
        create(Builder('news')
               .titled(u'Bookings open')
               .having(effectiveDate=DateTime(1999, 11, 15))
               .within(news_folder))

        # Visit the content page containing the news portlet. The old news
        # entry will not be rendered in the portlet due to the config of the
        # news portlet.
        browser.login().visit(content_page)

        # Clicking on the 'More News' link should render a page containing
        # the news entry.
        browser.find('More News').click()
        self.assertEquals(['Bookings open'],
                          browser.css('h2.tileHeadline').text)

    @browsing
    def test_news_listing_title(self, browser):
        """
        This test makes sure that the news listing view renders the
        title of the portlet, not the generic title.
        """
        folder = create(Builder('news folder').titled(u'News'))
        create(Builder('news').titled(u'Bookings open').within(folder))

        create(Builder('news portlet')
               .in_manager(u'plone.rightcolumn')
               .having(portlet_title=u'Breaking News',
                       current_context=False,
                       path=['/{0}'.format(folder.getId())],
                       show_more_news_link=True))

        browser.login().open()
        browser.find('More News').click()
        self.assertEquals(
            ['Breaking News'],
            browser.css('h1.documentFirstHeading').text
        )

    @browsing
    def test_news_listing_no_description(self, browser):
        """
        This test makes sure that the news listing view does not
        render the generic description.
        """
        content_page = create(Builder('sl content page')
                              .titled(u'My Page')
                              .having(description=u'My Description'))

        folder = create(Builder('news folder').titled(u'News'))
        create(Builder('news').titled(u'Bookings open').within(folder))

        create(Builder('news portlet')
               .within(content_page)
               .in_manager(u'plone.rightcolumn')
               .having(current_context=False,
                       path=['/{0}'.format(folder.getId())],
                       show_more_news_link=True))

        browser.login().visit(content_page)
        browser.find('More News').click()
        self.assertEquals(
            0,
            len(browser.css('div.documentDescription'))
        )

    @browsing
    def test_all_news(self, browser):
        """
        This test makes sure that the number of news entries is not limited
        when rendering "all news".
        """

        # Create a news portlet which limits the number of news entries to one.
        create(Builder('news portlet')
               .in_manager(u'plone.rightcolumn')
               .within(self.portal)
               .having(portlet_title=u'Aktuell',
                       show_more_news_link=True,
                       quantity=1))

        # Create a content page having a news folder.
        content_page = create(Builder('sl content page')
                              .titled(u'My Content Page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News')
                             .within(content_page))

        # Create two news entries.
        create(Builder('news').titled(u'News item 1').within(news_folder))
        create(Builder('news').titled(u'News item 2').within(news_folder))

        # Visit the content page containing the news portlet.
        browser.login().visit(content_page)

        # Clicking on the 'More News' link should render a page containing
        # both news entries.
        browser.find('More News').click()
        self.assertEquals(
            2,
            len(browser.css('div.newsListing div.tileItem'))
        )
