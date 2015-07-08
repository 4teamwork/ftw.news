from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder, create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.utils import getToolByName
import transaction
import unittest2 as unittest


news_portlet_action = '/++contextportlets++plone.rightcolumn/+/newsportlet'


class TestNewsPortlets(unittest.TestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        today = datetime.today()

        self.news_folder_1 = create(Builder('news folder')
                                    .titled(u'News Folder 1'))

        self.content_page = create(Builder('sl content page')
                                   .titled(u'Content Page'))
        self.news_folder_2 = create(Builder('news folder')
                                    .titled(u'News Folder 2')
                                    .within(self.content_page))

        description = u"This description must be longer than 50 characters " \
                      u"so we are able to test if it will be cropped."
        self.news_1 = create(Builder('news').titled(u'News Entry 1')
                             .within(self.news_folder_1)
                             .having(effective=today-timedelta(days=1),
                                     description=description,
                                     subjects=['Foo', 'Bar'],
                                     )
                             )
        self.news_2 = create(Builder('news').titled(u'News Entry 2')
                             .within(self.news_folder_1)
                             .having(effective=today-timedelta(days=15),
                                     description=description,
                                     subjects=['Hans', 'Peter'],
                                     )
                             )

        self.news_3 = create(Builder('news').titled(u'News Entry 3')
                             .within(self.news_folder_2)
                             .having(effective=today-timedelta(days=100),
                                     description=description)
                             )
        self.news_4 = create(Builder('news').titled(u'News Entry 4')
                             .within(self.news_folder_2)
                             .having(effective=today+timedelta(days=5),
                                     description=description)
                             )

    def _add_portlet(self, browser, **kwargs):
        browser.login().open()
        browser.visit(self.portal, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()
        browser.fill(kwargs).save()
        browser.open()

    @browsing
    def test_add_form_cancel(self, browser):
        browser.login().open(self.portal.absolute_url() + news_portlet_action)
        browser.find('form.buttons.cancel_add').click()
        self.assertEqual(self.portal.absolute_url() + '/@@manage-portlets',
                         browser.url)

    @browsing
    def test_edit_form_success(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet'})

        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u'Changed Title'}).save()

        self.assertEqual(self.portal.absolute_url() + '/@@manage-portlets',
                         browser.url)
        self.assertEqual('News Portlet (Changed Title)',
                         browser.find('News Portlet (Changed Title)').text)

    @browsing
    def test_edit_form_cancel(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet'})

        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u'Change Title Without Saving'})
        browser.find('form.buttons.cancel_add').click()

        self.assertEqual(self.portal.absolute_url() + '/@@manage-portlets',
                         browser.url)
        self.assertIsNone(
            browser.find('News Portlet (Change Title Without Saving)'))

    @browsing
    def test_edit_form_error_missing_title(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet'})

        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u''}).save()

        assert_message('There were some errors.')
        self.assertIn(u'Title Required input is missing.',
                      browser.css('div.error').text)

    @browsing
    def test_portlet_prevents_path_and_current_context(self, browser):
        browser.login().visit(self.portal, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()

        form_data = {'Title': 'A News Portlet',
                     'Limit to path': self.news_folder_1,
                     'Limit to current context': True}
        browser.fill(form_data).save()

        assert_message('There were some errors.')
        self.assertEqual('You can not filter by path and current '
                         'context at the same time.',
                         browser.css('div#content-core div.error '
                                     'div.error').first.text)

    @browsing
    def test_portlet_does_not_filter_current_context(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet',
                                      'Limit to current context': False})
        self.assertEqual(4, len(browser.css('li.portletItem')))

        browser.visit(self.content_page)
        self.assertEqual(4, len(browser.css('li.portletItem')))

    @browsing
    def test_portlet_filters_current_context(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet',
                                      'Limit to current context': True})
        self.assertEqual(4, len(browser.css('li.portletItem')))

        browser.visit(self.content_page)
        self.assertIn(self.news_3.absolute_url(), browser.contents)
        self.assertIn(self.news_4.absolute_url(), browser.contents)
        self.assertFalse(self.news_1.absolute_url() in browser.contents)
        self.assertFalse(self.news_2.absolute_url() in browser.contents)

    @browsing
    def test_portlet_filters_path(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet',
                                      'Limit to path': self.news_folder_2,
                                      'Limit to current context': False})
        self.assertFalse(self.news_1.absolute_url() in browser.contents)
        self.assertFalse(self.news_2.absolute_url() in browser.contents)
        self.assertEqual(self.news_4.absolute_url(),
                         browser.css('li.portletItem a').first.attrib['href'])
        self.assertEqual(self.news_3.absolute_url(),
                         browser.css('li.portletItem a')[1].attrib['href'])

    @browsing
    def test_portlet_crops_description(self, browser):
        self._add_portlet(browser, **{'Title': 'A News Portlet'})
        self.assertIn('This description must be longer than 50 ... Read more',
                      browser.css('li.portletItem').first.text)

    @browsing
    def test_portlet_does_not_render_description(self, browser):
        form_values = {
            'Title': 'A News Portlet',
            'Show the description of the news item': False,
        }
        self._add_portlet(browser, **form_values)
        self.assertFalse('This description' in
                         browser.css('li.portletItem').first.text)

    @browsing
    def test_portlet_filters_by_subject(self, browser):
        form_values = {
            'Title': 'A News Portlet',
            'Filter by subject': 'Foo',
        }
        self._add_portlet(browser, **form_values)
        self.assertEqual(1, len(browser.css('li.portletItem')))
        self.assertEqual(
            'http://nohost/plone/news-folder-1/news-entry-1',
            browser.css('li.portletItem a').first.attrib['href']
        )

    @browsing
    def test_portlet_filters_old_news(self, browser):
        form_values = {
            'Title': 'A News Portlet',
            'Maximum age (days)': u'50',
        }
        self._add_portlet(browser, **form_values)
        self.assertEquals(3, len(browser.css('li.portletItem')))

    @browsing
    def test_portlet_renders_more_link_when_enabled(self, browser):
        form_values = {
            'Title': 'A News Portlet',
            'Link to more news': True,
        }
        self._add_portlet(browser, **form_values)
        self.assertNotEquals(None, browser.find('More News'))

    @browsing
    def test_portlet_does_not_render_more_link_when_disabled(self, browser):
        form_values = {
            'Title': 'A News Portlet',
            'Link to more news': False,
        }
        self._add_portlet(browser, **form_values)
        self.assertIsNone(browser.find('More News'))

    @browsing
    def test_portlet_renders_rss_link_when_enabled(self, browser):
        form_values = {
            'Title': u'A News Portlet',
            'Link to RSS feed': True,
        }
        self._add_portlet(browser, **form_values)
        self.assertNotEquals(None, browser.find('RSS'))

    @browsing
    def test_portlet_does_not_render_rss_link_when_disabled(self, browser):
        form_values = {
            'Title': u'A News Portlet',
            'Link to RSS feed': False,
        }
        self._add_portlet(browser, **form_values)
        self.assertIsNone(browser.find('RSS'))

    @browsing
    def test_portlet_is_not_available_without_news_entries(self, browser):
        form_values = {
            'Title': u'A News Portlet',
            'Always render the portlet': False,
        }
        self._add_portlet(browser, **form_values)
        self.assertIsNone(browser.find('More News'))

    @browsing
    def test_portlet_is_available_without_news_entries(self, browser):
        empty_folder = create(Builder('news folder')
                              .titled(u'Empty news folder'))

        form_values = {
            'Title': u'A News Portlet',
            'Always render the portlet': True,
            'Limit to path': empty_folder,
            'Limit to current context': False,
            'Link to more news': True,
        }
        self._add_portlet(browser, **form_values)

        self.assertIn('No recent news available.',
                      browser.css('.noRecentNews').text)
        self.assertEqual('More News', browser.find('More News').text)
