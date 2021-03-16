import re
from datetime import datetime

import transaction
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.behaviors.mopage import IMopageModificationDate
from ftw.news.tests import utils
from ftw.news.tests.base import FunctionalTestCase
from ftw.news.tests.base import XMLDiffTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testing import IS_PLONE_5
from ftw.testing import freeze
from ftw.testing import staticuid
from path import Path
from plone.app.textfield import RichTextValue
from Products.CMFCore.utils import getToolByName


class TestMopageExport(FunctionalTestCase, XMLDiffTestCase):

    @staticuid('uid')
    @browsing
    def test_01_export_news(self, browser):
        self.grant('Manager')
        news_folder = create(Builder('news folder').titled(u'News Folder'))

        with freeze(datetime(2010, 3, 14, 20, 18)):
            news1 = create(
                Builder('news')
                .titled(u'Usain Bolt at the \xd6lympics')
                .within(news_folder)
                .having(news_date=datetime(2010, 3, 15, 12, 00),
                        description=u'Usain Bolt wins the \xd6lympic gold in'
                        u' three events.\n\nThe third is for a 100-metre relay.',
                        subjects=('Homepage', 'Sports')))

            lorem = RichTextValue(self.asset('lorem1.html'))
            block = create(Builder('sl textblock').within(news1)
                           .with_dummy_image()
                           .having(text=lorem))
            utils.create_page_state(news1, block)
            IMopageModificationDate(news1).set_date(DateTime('2010/3/15'))

        with freeze(datetime(2010, 5, 17, 15, 34)):
            create(Builder('news')
                   .titled(u'Largest Aircraft in the World')
                   .within(news_folder)
                   .having(news_date=datetime(2010, 5, 18, 12, 00),
                           expires=datetime(2020, 1, 1)))

        # listing block should not appear in endpoint
        listingblock = create(Builder('sl listingblock')
                              .titled('My listingblock')
                              .having(show_title=True)
                              .within(news1))

        create(Builder('file').with_dummy_content().within(listingblock))

        with freeze(datetime(2011, 1, 2, 3, 4)):
            if IS_PLONE_5:
                self.assert_mopage_export('01_export_news_plone5.xml', news_folder)
            else:
                self.assert_mopage_export('01_export_news.xml', news_folder)

    @browsing
    def test_pagination(self, browser):
        self.grant('Manager')
        news_folder = create(Builder('news folder').titled(u'News'))
        with freeze(datetime(2015, 10, 1)) as clock:
            create(Builder('news').titled(u'One').within(news_folder))
            clock.forward(days=1)
            create(Builder('news').titled(u'Two').within(news_folder))
            clock.forward(days=1)
            create(Builder('news').titled(u'Three').within(news_folder))
            clock.forward(days=1)
            create(Builder('news').titled(u'Four').within(news_folder))
            clock.forward(days=1)
            create(Builder('news').titled(u'Five').within(news_folder))

        browser.open(news_folder, view='mopage.news.xml?per_page=2')
        self.assert_news_in_browser(['Five', 'Four'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'next': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=2',
             'last': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=3'},
            links)

        browser.open(links['next'])
        self.assert_news_in_browser(['Three', 'Two'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'first': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=1',
             'prev': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=1',
             'next': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=3',
             'last': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=3'},
            links)

        browser.open(links['next'])
        self.assert_news_in_browser(['One'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'first': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=1',
             'prev': 'http://nohost/plone/news/mopage.news.xml?per_page=2&page=2'},
            links)

    @browsing
    def test_export_all_news_on_site(self, browser):
        self.grant('Manager')
        with freeze(datetime(2015, 10, 1)) as clock:
            create(Builder('news').titled(u'One').within(
                create(Builder('news folder').titled(u'News Folder One'))))
            clock.forward(days=1)
            create(Builder('news').titled(u'Two').within(
                create(Builder('news folder').titled(u'News Folder Two'))))

        browser.open(self.portal, view='mopage.news.xml')
        self.assert_news_in_browser(['Two', 'One'])

    @browsing
    def test_title_is_cropped(self, browser):
        self.grant('Manager')
        create(Builder('news').titled(u'A' * 150).within(
            create(Builder('news folder'))))

        browser.open(self.portal, view='mopage.news.xml')
        self.assert_news_in_browser(['A' * 95 + ' ...'])

    @browsing
    def test_text_cropped_to_max_10000_chars(self, browser):
        self.grant('Manager')
        create(Builder('sl textblock')
               .having(text=RichTextValue('a' * 20000))
               .within(
                   create(Builder('news').titled(u'A').within(
                       create(Builder('news folder'))))))

        create(Builder('sl textblock')
               .having(text=RichTextValue('a' * 100000))
               .within(
                   create(Builder('news').titled(u'B').within(
                       create(Builder('news folder'))))))

        browser.open(self.portal, view='mopage.news.xml')
        texts = browser.css('textmobile').text

        self.assertEquals(
            'a' * 7995 + ' ...',  # 10000 - (textlength * 0.1) - 5
            texts[0],
            'Text should be cropped to a max of 10000 chars'
        )

        self.assertEquals(
            'a' * 9995 + ' ...',  # if (textlength * 0.1 > 9000) crop at 10000 - 5
            texts[1],
            'The text shouldn\'t be cropped to be smaller than 1000 chars if possible'
        )

    @browsing
    def test_include_root_arguments_when_submitted_as_GET_param(self, browser):
        self.grant('Manager')
        create(Builder('news').within(create(Builder('news folder'))))

        with freeze(datetime(2016, 8, 9, 21, 45)):
            browser.open(self.portal, view='mopage.news.xml',
                         data={'partner': 'Partner',
                               'partnerid': '123',
                               'passwort': 's3c>r3t',
                               'importid': '456',
                               'vaterobjekt': 'xy',
                               'unkown_key': 'should not appear'})

        self.assertEquals(
            {
                'export_time': '2016-08-09 21:45:00',
                'partner': 'Partner',
                'partnerid': '123',
                'passwort': 's3c>r3t',
                'importid': '456',
                'vaterobjekt': 'xy',
            },
            browser.css('import').first.attrib)

    def assert_mopage_export(self, asset_name, export_context):
        expected = self.asset(asset_name)
        browser.open(export_context, view='mopage.news.xml')
        got = browser.contents
        # replace dynamic scale image urls for having static test results:
        got = re.sub(r'\/@@images/[a-z0-9-]{36}.jpeg', '/image.jpg', got)
        # remove trailing spaces:
        got = re.sub(r' +$', '', got, flags=re.M)
        self.maxDiff = None
        self.assert_xml(expected, got)

    def asset(self, asset_name):
        assets = Path(__file__).joinpath('..', 'mopage_assets').abspath()
        return assets.joinpath(asset_name).bytes()

    def assert_news_in_browser(self, expected_titles):
        got_titles = browser.css('titel').text
        self.assertEquals(expected_titles, got_titles)

    def get_links_from_response(self):
        def parse_link(text):
            return tuple(reversed(re.match(
                r'^<([^>]+)>; rel="([^"]+)"', text).groups()))

        return dict(map(parse_link, browser.headers.get('Link').split(',')))

    @browsing
    def test_custom_external_url(self, browser):
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types['ftw.news.News'].behaviors += (
            'ftw.news.behaviors.external_url.INewsExternalUrl',
        )
        transaction.commit()

        self.grant('Manager')
        create(Builder('news')
               .titled(u'A news item having a custom external url')
               .having(external_url=u'http://www.4teamwork.ch/')
               .within(create(Builder('news folder'))))

        browser.open(self.portal, view='mopage.news.xml')
        self.assertEqual(
            ['http://www.4teamwork.ch/'],
            browser.css('url_web').text
        )
