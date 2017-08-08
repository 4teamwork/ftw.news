from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.news.behaviors.show_on_homepage.news import IShowOnHomepage
from ftw.news.behaviors.show_on_homepage.news import IShowOnHomepageSchema
from ftw.news.tests.base import FunctionalTestCase
from ftw.testbrowser import browsing
from plone.app.testing import applyProfile
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import Interface


class TestNewsOnHomepageBehavior(FunctionalTestCase):

    def setUp(self):
        super(TestNewsOnHomepageBehavior, self).setUp()
        self.grant('Manager')

    @browsing
    def test_show_on_home_field_is_protected(self, browser):
        applyProfile(self.portal, 'ftw.news:show-on-homepage')

        page = create(Builder('sl content page'))
        newsfolder = create(Builder('news folder').within(page))
        news = create(Builder('news')
                      .within(newsfolder)
                      .having(news_date=datetime(2011, 1, 2, 15, 0, 0)))

        field_label = 'Show on home page'

        browser.login().visit(news, view='edit')
        self.assertIn(
            field_label,
            browser.forms['form'].field_labels,
            "The manager must be able to mark news to be shown on the"
            "homepage,"
        )

        user = create(Builder('user').with_roles('Editor'))
        browser.login(user).visit(news, view='edit')
        self.assertNotIn(
            field_label,
            browser.forms['form'].field_labels,
            "An editor must not be able to mark news to be shown on the"
            "homepage."
        )

    def test_show_on_home_factory_does_not_remove_other_interfaces(self):
        applyProfile(self.portal, 'ftw.news:show-on-homepage')

        page = create(Builder('sl content page'))
        newsfolder = create(Builder('news folder').within(page))
        news = create(Builder('news')
                      .within(newsfolder)
                      .having(news_date=datetime(2011, 1, 2, 15, 0, 0)))

        class IDummyMarkerInterface(Interface):
            pass

        directlyProvides(news, IDummyMarkerInterface)
        self.assertEqual(
            [IDummyMarkerInterface],
            list(directlyProvidedBy(news))
        )

        IShowOnHomepageSchema(news).show_on_homepage = True
        self.assertEqual(
            [IDummyMarkerInterface, IShowOnHomepage],
            list(directlyProvidedBy(news))
        )

        IShowOnHomepageSchema(news).show_on_homepage = False
        self.assertEqual(
            [IDummyMarkerInterface],
            list(directlyProvidedBy(news))
        )
