from collective.taskqueue.testing import runAsyncTest
from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.behaviors.mopage import IMopageModificationDate
from ftw.news.behaviors.mopage import IPublisherMopageTrigger
from ftw.news.testing import MOPAGE_TRIGGER_FUNCTIONAL
from ftw.news.tests.base import FunctionalTestCase
from ftw.publisher.receiver.events import AfterCreatedEvent
from ftw.publisher.receiver.events import AfterUpdatedEvent
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
import transaction
import urlparse


def get_stub_log(portal):
    annotations = IAnnotations(portal)
    key = 'ftw.news-mopage-stub-log'
    if key not in annotations:
        annotations[key] = PersistentList()
    return annotations[key]


class MopageAPIStub(BrowserView):

    def __call__(self):
        log = get_stub_log(self.context)
        log.append(self.request.form)
        return 'OK'


class TestMopageTrigger(FunctionalTestCase):
    layer = MOPAGE_TRIGGER_FUNCTIONAL

    def setUp(self):
        super(TestMopageTrigger, self).setUp()

        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types['ftw.news.NewsFolder'].behaviors += (
            'ftw.news.behaviors.mopage.IPublisherMopageTrigger',
        )
        transaction.commit()

    @browsing
    def test_configure_trigger_on_news_folder(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('News Folder')
        browser.fill(
            {'Title': 'News Folder',
             'Mopage trigger enabled': True,
             'Mopage trigger URL': (
                 'https://un:pw@xml.mopage.ch/infoservice/xml.php'),
             'Mopage data endpoint URL (Plone)': (
                 'http://nohost/plone/news-folder/mopage.news.xml'
                 '?partnerid=123&imported=456')}).save()

        statusmessages.assert_no_error_messages()

        mopage_trigger = IPublisherMopageTrigger(browser.context)
        self.assertTrue(mopage_trigger.is_enabled())

        trigger_url = mopage_trigger.build_trigger_url()
        self.assertEquals('https://un:pw@xml.mopage.ch/infoservice/xml.php'
                          '?url=http%3A%2F%2Fnohost%2Fplone%2Fnews-folder'
                          '%2Fmopage.news.xml%3Fpartnerid%3D123%26imported%3D456',
                          trigger_url)

        params =  urlparse.parse_qs(urlparse.urlparse(trigger_url)[4])['url']
        self.assertEquals(['http://nohost/plone/news-folder/'
                           'mopage.news.xml?partnerid=123&imported=456'],
                          params)

    def test_trigger_notified_when_news_created(self):
        self.grant('Manager')
        trigger_url = self.portal.portal_url() + '/mopage-stub'
        endpoint_url = (self.portal.portal_url() + '/news-folder/mopage.news.xml' +
                        '?partnerid=213&importid=456')

        folder = create(Builder('news folder')
                        .titled(u'News Folder')
                        .having(mopage_enabled=True,
                                mopage_trigger_url=trigger_url,
                                mopage_data_endpoint_url=endpoint_url))

        news = create(Builder('news').titled(u'The News').within(folder))
        self.assertEquals([], get_stub_log(self.portal))

        notify(AfterCreatedEvent(news))
        transaction.commit()
        runAsyncTest(lambda: None)
        transaction.begin()
        self.assertEquals(
            [{'url': endpoint_url}],
            get_stub_log(self.portal))

    def test_trigger_notified_when_news_updated(self):
        self.grant('Manager')
        trigger_url = self.portal.portal_url() + '/mopage-stub'
        endpoint_url = (self.portal.portal_url() + '/news-folder/mopage.news.xml' +
                        '?partnerid=999&importid=888')

        folder = create(Builder('news folder')
                        .titled(u'News Folder')
                        .having(mopage_enabled=True,
                                mopage_trigger_url=trigger_url,
                                mopage_data_endpoint_url=endpoint_url))

        news = create(Builder('news').titled(u'The News').within(folder))
        self.assertEquals([], get_stub_log(self.portal))

        notify(AfterUpdatedEvent(news))
        transaction.commit()
        runAsyncTest(lambda: None)
        transaction.begin()
        self.assertEquals(
            [{'url': endpoint_url}],
            get_stub_log(self.portal))

    def test_trigger_notified_when_sl_block_is_created_in_a_news(self):
        """When a news is published, the first page is the news, then
        the content of the news follows in separate jobs (sl blocks,
        recursive structures).
        When we only trigger when the news itself is published, the content
        will be missing.
        Therefore we must trigger an update on any change within the news.
        """
        self.grant('Manager')
        trigger_url = self.portal.portal_url() + '/mopage-stub'
        endpoint_url = (self.portal.portal_url() + '/news-folder/mopage.news.xml' +
                        '?partnerid=213&importid=456')

        folder = create(Builder('news folder')
                        .titled(u'News Folder')
                        .having(mopage_enabled=True,
                                mopage_trigger_url=trigger_url,
                                mopage_data_endpoint_url=endpoint_url))

        news = create(Builder('news').titled(u'The News').within(folder))
        block = create(Builder('sl textblock').within(news))

        self.assertEquals([], get_stub_log(self.portal))

        notify(AfterCreatedEvent(block))
        transaction.commit()
        runAsyncTest(lambda: None)
        transaction.begin()
        self.assertEquals(
            [{'url': endpoint_url}],
            get_stub_log(self.portal))

    def test_publisher_event_updates_mopage_modified_date(self):
        """The idea of the mopage modified date is that it tracks modifications
        on the content, more specific blocks added by publisher.
        This is important in order to tell the mopage system that things have
        changed.
        However, it is not the Plone modification date and it should be updated
        by the publisher subscriber.
        """
        self.grant('Manager')
        trigger_url = self.portal.portal_url() + '/mopage-stub'
        endpoint_url = (self.portal.portal_url() + '/news-folder/mopage.news.xml' +
                        '?partnerid=213&importid=456')
        folder = create(Builder('news folder')
                        .having(mopage_enabled=True,
                                mopage_trigger_url=trigger_url,
                                mopage_data_endpoint_url=endpoint_url))

        with freeze(datetime(2016, 1, 1)) as clock:
            news = create(Builder('news').within(folder))
            block = create(Builder('sl textblock').within(news))
            self.assertEquals(DateTime('2016/1/1'),
                              IMopageModificationDate(news).get_date())

            clock.forward(days=1)
            notify(AfterCreatedEvent(block))
            self.assertEquals(DateTime('2016/1/2'),
                              IMopageModificationDate(news).get_date())

            clock.forward(days=1)
            news.setModificationDate(DateTime())
            notify(AfterCreatedEvent(block))
            self.assertEquals(DateTime('2016/1/3'),
                              IMopageModificationDate(news).get_date())
