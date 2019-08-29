from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from ftw.news.tests.utils import LanguageSetter
from ftw.testbrowser import browsing
from zope.i18n.locales import locales


news_portlet_action = '/++contextportlets++plone.rightcolumn/+/' \
                      'newsarchiveportlet'


class TestNewsArchivePortlets(FunctionalTestCase, LanguageSetter):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsArchivePortlets, self).setUp()
        self.grant('Manager')

        default = 'en'
        supported = ['en', 'de']
        self.set_language_settings(default, supported)

    def _set_language_de(self):
        """This Function is used to set the language of the plone site.
        We need this, because we wan't to make sure that the language is
        inherited when there isn't one forced.
        """
        locale = locales.getLocale('de')
        target_language = locale.id.language

        # If we get a territory, we enable the combined language codes
        use_combined = False
        if locale.id.territory:
            use_combined = True
            target_language += '_' + locale.id.territory

        # As we have a sensible language code set now, we disable the
        # start neutral functionality (not available in plone 5.1 anymore).
        start_neutral = False

        self.set_language_settings(target_language, [target_language],
                                   use_combined, start_neutral)

    def _add_portlet(self, browser, context=None):
        """
        This helper method adds a news archive portlet on the given context.
        If no context is provided then the portlet will be added on the
        Plone site.
        """
        context = context or self.portal
        browser.login().visit(context, view='@@manage-portlets')
        browser.css('#portletmanager-plone-rightcolumn form')[0].fill(
            {':action': news_portlet_action}).submit()
        browser.css('#form').first.fill({'Title': 'Archive'}).submit()
        browser.open(context)

    @browsing
    def test_archive_portlet_available_when_there_are_news(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
        create(Builder('news').titled(u'News Entry').within(news_folder)
               .with_property('layout', 'news_listing'))

        self._add_portlet(browser, news_folder)

        self.assertIn('Archive', browser.css('.archive-portlet header h2').text,
                      'Archive portlet is not here but it should be.')

    @browsing
    def test_archive_portlet_not_available_when_empty(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))

        self._add_portlet(browser, news_folder)

        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_summary(self, browser):
        """
        This test makes sure the summary is correct.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
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
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
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
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder))

        self._add_portlet(browser, page)
        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_link(self, browser):
        """
        This test makes sure the summary is correct.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder)
               .having(news_date=datetime(2013, 1, 1)))
        create(Builder('news').titled(u'News Entry 2').within(news_folder)
               .having(news_date=datetime(2013, 1, 11)))

        self._add_portlet(browser, news_folder)

        browser.css('.month').first.click()
        self.assertEqual(2, len(browser.css('.news-item')))

    @browsing
    def test_month_with_umlaut(self, browser):
        self._set_language_de()

        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .with_property('layout', 'news_listing'))
        create(Builder('news').titled(u'News Entry 1').within(news_folder)
               .having(news_date=datetime(2013, 3, 1)))

        # Helper method sets the title in english and not in german
        browser.login().visit(news_folder, view='@@manage-portlets')
        browser.css('#portletmanager-plone-rightcolumn form')[0].fill(
            {':action': news_portlet_action}).submit()
        browser.css('#form').first.fill({'Titel': 'Archiv'}).submit()
        browser.open(news_folder)

        browser.css('.month').first.click()
        self.assertEqual(1, len(browser.css('.news-item')))
