from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone import api
import transaction


news_portlet_action = '/++contextportlets++plone.rightcolumn/+/' \
                      'newsarchiveportlet'


class TestNewsArchivePortlets(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsArchivePortlets, self).setUp()
        self.grant('Manager')

    def _add_portlet(self, browser, context=None):
        """
        This helper method adds a news archive portlet on the given context.
        If no context is provided then the portlet will be added on the
        Plone site.
        """
        context = context or self.portal
        browser.login().visit(context, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()
        browser.open(context)

    @browsing
    def test_archive_portlet_available_when_there_are_news(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry').within(news_folder))

        self._add_portlet(browser, news_folder)

        self.assertIn('Archive', browser.css('.archive-portlet header h2').text,
                      'Archive portlet is not here but it should be.')

    @browsing
    def test_archive_portlet_not_available_when_empty(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))

        self._add_portlet(browser, news_folder)

        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_summary(self, browser):
        """
        This test makes sure the summary is correct.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder)
               .having(news_date=datetime(2013, 1, 1)))
        create(Builder('news').titled(u'News Entry 2').within(news_folder)
               .having(news_date=datetime(2013, 1, 11)))
        create(Builder('news').titled(u'News Entry 3').within(news_folder)
               .having(news_date=datetime(2013, 2, 2)))
        create(Builder('news').titled(u'News Entry 5').within(news_folder)
               .having(news_date=None))

        self._add_portlet(browser, news_folder)

        self.assertEqual(
            ['http://nohost/plone/news-folder/news_listing?archive=2013/02/01',
             'http://nohost/plone/news-folder/news_listing?archive=2013/01/01'],
            map(lambda month: month.attrib['href'], browser.css('.month')))

    @browsing
    def test_archive_portlet_not_available_on_plone_site(self, browser):
        """
        The news archive portlet is only rendered on news listing views.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder))

        self._add_portlet(browser)
        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_not_available_on_content_page(self, browser):
        """
        The news archive portlet is only rendered on news listing views.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder))

        self._add_portlet(browser, page)
        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_link(self, browser):
        """
        This test makes sure the summary is correct.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder)
               .having(news_date=datetime(2013, 1, 1)))
        create(Builder('news').titled(u'News Entry 2').within(news_folder)
               .having(news_date=datetime(2013, 1, 11)))

        self._add_portlet(browser, news_folder)

        browser.css('.month').first.click()
        self.assertEqual(2, len(browser.css('.news-item')))

    @browsing
    def test_month_with_umlaut(self, browser):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        transaction.commit()

        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder)
               .having(news_date=datetime(2013, 3, 1)))

        self._add_portlet(browser, news_folder)

        browser.css('.month').first.click()
        self.assertEqual(1, len(browser.css('.news-item')))
