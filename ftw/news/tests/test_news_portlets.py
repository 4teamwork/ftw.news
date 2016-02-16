from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder, create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests import FunctionalTestCase
from ftw.news.tests import utils
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message


news_portlet_action = '/++contextportlets++plone.rightcolumn/+/newsportlet'


class TestNewsPortlets(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNewsPortlets, self).setUp()
        self.grant('Manager')

    def _add_portlet(self, browser, context=None, **kwargs):
        """
        This helper method adds a news portlet on the given context.
        If no context is provided then the portlet will be added on the
        Plone site.
        After adding the portlet the browser navigates to the context.
        """
        context = context or self.portal
        browser.login().visit(context, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()
        browser.forms['form'].fill(kwargs).save()
        browser.visit(context)

    @browsing
    def test_add_portlet_on_content_page(self, browser):
        """
        This test makes sure that the portlet can be created on
        a content page and that the portlet renders a news entry.
        """
        # Create some content and the portlet
        page = create(Builder('sl content page').titled(u'Content Page'))
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .within(page))
        create(Builder('news').titled(u'Hello World').within(news_folder))
        self._add_portlet(browser, page, **{'Title': 'A News Portlet'})

        self.assertEqual(1, len(browser.css('.news-item')))
        self.assertIn('Hello World', browser.css('.news-item').first.text)

    @browsing
    def test_add_portlet_on_plone_root(self, browser):
        """
        This test makes sure that the portlet can be created on
        a content page and that the portlet renders a news entry.
        """
        # Create some content and the portlet
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .within(self.portal))
        create(Builder('news').titled(u'Hello World').within(news_folder))
        self._add_portlet(browser, self.portal, **{'Title': 'A News Portlet'})

        self.assertEqual(1, len(browser.css('.news-item')))
        self.assertIn('Hello World', browser.css('.news-item').first.text)

    @browsing
    def test_portlet_add_form_cancel_button(self, browser):
        """
        This test makes sure that cancelling the creation of the portlet
        does not create the portlet.
        """
        context = self.portal
        self._add_portlet(browser, context, **{'Title': 'A News Portlet'})

        # Make sure the portlet is available on @@manage-portlets.
        browser.login().visit(context, view='@@manage-portlets')
        self.assertEqual(1, len(browser.css('div.portletAssignments '
                                            'div.managedPortlet.portlet')))

        # Go to the portlet add form to add a second portlet
        # but cancel the creation.
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()
        browser.find('form.buttons.cancel').click()

        # Make sure there is still only one portlet.
        self.assertEqual(1, len(browser.css('div.portletAssignments '
                                            'div.managedPortlet.portlet')))

    @browsing
    def test_portlet_edit_form_success(self, browser):
        """
        This test makes sure that editing an existing portlet works.
        """
        context = self.portal
        self._add_portlet(browser, context, **{'Title': 'A News Portlet'})

        # Edit the portlet.
        browser.visit(context, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u'Changed Title'}).save()

        self.assertEqual(self.portal.absolute_url() + '/@@manage-portlets',
                         browser.url)
        self.assertEqual('News Portlet (Changed Title)',
                         browser.find('News Portlet (Changed Title)').text)

    @browsing
    def test_portlet_edit_form_cancel(self, browser):
        """
        This test makes sure that cancelling the editing of a portlet does
        not change the portlet.
        """
        context = self.portal
        self._add_portlet(browser, context, **{'Title': 'A News Portlet'})

        # Start editing the portlet.
        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u'Change Title Without Saving'}).submit()
        browser.find('form.buttons.cancel_add').click()

        self.assertEqual(self.portal.absolute_url() + '/@@manage-portlets',
                         browser.url)
        self.assertIsNone(
            browser.find('News Portlet (Change Title Without Saving)'))

    @browsing
    def test_portlet_edit_form_error_missing_title(self, browser):
        """
        This test makes sure that the title of the portlet is mandatory
        when editing the portlet.
        """
        context = self.portal
        self._add_portlet(browser, context, **{'Title': 'A News Portlet'})

        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Title': u''}).save()

        assert_message('There were some errors.')
        self.assertIn(u'Title Required input is missing.',
                      browser.css('div.error').text)

    @browsing
    def test_portlet_prevents_path_and_current_context(self, browser):
        """
        This test makes sure that a portlet cannot have filters by path
        and current context at the same time.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        browser.login().visit(self.portal, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()

        form_data = {'Title': 'A News Portlet',
                     'Limit to path': news_folder,
                     'Limit to current context': True}
        browser.fill(form_data).save()

        assert_message('There were some errors.')
        self.assertEqual('You can not filter by path and current '
                         'context at the same time.',
                         browser.css('div#content-core div.error '
                                     'div.error').first.text)

    @browsing
    def test_portlet_does_not_filter_current_context(self, browser):
        """
        This test makes sure the portlet does not filter by current context
        if told to not do so.
        """
        page1 = create(Builder('sl content page').titled(u'Content Page 1'))
        news_folder1 = create(Builder('news folder').titled(u'News Folder 1')
                              .within(page1))
        create(Builder('news').titled(u'Hello World 1').within(news_folder1))

        page2 = create(Builder('sl content page').titled(u'Content Page 2'))
        news_folder2 = create(Builder('news folder').titled(u'News Folder 2')
                              .within(page2))
        create(Builder('news').titled(u'Hello World 2').within(news_folder2))

        # Create the portlet on page 2.
        portlet_config = {
            'Title': 'A News Portlet',
            'Limit to current context': False,
        }
        self._add_portlet(browser, page2, **portlet_config)

        self.assertEqual(2, len(browser.css('.news-item')))

    @browsing
    def test_portlet_filters_current_context(self, browser):
        """
        This test makes sure the portlet only renders news entries from
        the current context if told to do so.
        """
        page1 = create(Builder('sl content page').titled(u'Content Page 1'))
        news_folder1 = create(Builder('news folder').titled(u'News Folder 1')
                              .within(page1))
        create(Builder('news').titled(u'Hello World 1').within(news_folder1))

        page2 = create(Builder('sl content page').titled(u'Content Page 2'))
        news_folder2 = create(Builder('news folder').titled(u'News Folder 2')
                              .within(page2))
        create(Builder('news').titled(u'Hello World 2').within(news_folder2))

        # Create the portlet on page 2.
        portlet_config = {
            'Title': 'A News Portlet',
            'Limit to current context': True,
        }
        self._add_portlet(browser, page2, **portlet_config)

        self.assertEqual(1, len(browser.css('.news-item')))
        self.assertIn('Hello World 2',
                      browser.css('.news-item .title').first.text)

    @browsing
    def test_portlet_filters_by_path(self, browser):
        """
        This test makes sure that the portlet only renders news entries
        from the path configured in the portlet.
        """
        page1 = create(Builder('sl content page').titled(u'Content Page 1'))
        news_folder1 = create(Builder('news folder').titled(u'News Folder 1')
                              .within(page1))
        create(Builder('news').titled(u'Hello World 1').within(news_folder1))

        page2 = create(Builder('sl content page').titled(u'Content Page 2'))
        news_folder2 = create(Builder('news folder').titled(u'News Folder 2')
                              .within(page2))
        create(Builder('news').titled(u'Hello World 2').within(news_folder2))

        # Create the portlet on plone root.
        portlet_config = {
            'Title': 'A News Portlet',
            'Limit to path': news_folder2,
            'Limit to current context': False,
        }
        self._add_portlet(browser, self.portal, **portlet_config)

        self.assertEqual(1, len(browser.css('.news-item')))
        self.assertIn('Hello World 2',
                      browser.css('.news-item .title').first.text)

    @browsing
    def test_portlet_crops_description(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        description = u"This description must be longer than 50 characters " \
                      u"so we are able to test if it will be cropped."
        create(Builder('news')
               .titled(u'Hello World')
               .within(news_folder)
               .having(description=description))

        self._add_portlet(browser, **{'Title': 'A News Portlet'})
        self.assertIn('This description must be longer than 50 ...',
                      browser.css('.news-item .description').first.text)

    @browsing
    def test_portlet_does_not_render_description(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World').within(news_folder)
               .having(description=u'This description'))

        # First make sure the description is rendered.
        portlet_config = {
            'Title': 'A News Portlet',
            'Show the description of the news item': True,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertIn('This description',
                      browser.css('.news-item .description').first.text)

        # Tell the portlet to not render the description anymore.
        browser.visit(self.portal, view='manage-portlets')
        browser.find('News Portlet (A News Portlet)').click()
        browser.fill({'Show the description of the news item': False}).save()

        # Make sure the description is not rendered.
        browser.visit(self.portal)
        self.assertNotIn('This description',
                         browser.css('.news-item').first.text)

    @browsing
    def test_portlet_filters_by_subject(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news')
               .titled(u'Hello World 1')
               .within(news_folder)
               .having(subjects=['Hans']))
        create(Builder('news').titled(u'Hello World 2').within(news_folder)
               .having(subjects=['Peter']))

        browser.login().visit(self.portal, view='@@manage-portlets')
        browser.forms['form-3'].fill({':action': news_portlet_action}).submit()

        subjects = browser.find('Filter by subject').query('Peter')
        portlet_config = {
            'Title': 'A News Portlet',
            'Filter by subject': subjects[0][0],
        }
        self._add_portlet(browser, **portlet_config)

        self.assertEqual(1, len(browser.css('.news-item .title')))
        self.assertIn('Hello World 2',
                      browser.css('.news-item').first.text)

    @browsing
    def test_portlet_filters_old_news(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))

        old = datetime.now() - timedelta(days=10)
        older = datetime.now() - timedelta(days=50)

        create(Builder('news')
               .titled(u'Hello World 1')
               .within(news_folder)
               .having(news_date=old))

        create(Builder('news')
               .titled(u'Hello World 2')
               .within(news_folder)
               .having(news_date=older))

        portlet_config = {
            'Title': 'A News Portlet',
            'Maximum age (days)': u'20',
            'Limit to current context': False,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertEquals(1, len(browser.css('.news-item')))

    @browsing
    def test_portlet_renders_more_link_when_enabled(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World 1').within(news_folder))

        portlet_config = {
            'Title': 'A News Portlet',
            'Link to more news': True,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertEqual('More News', browser.find('More News').text)

    @browsing
    def test_portlet_does_not_render_more_link_when_disabled(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World 1').within(news_folder))

        portlet_config = {
            'Title': 'A News Portlet',
            'Link to more news': False,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertIsNone(browser.find('More News'))

    @browsing
    def test_portlet_renders_rss_link_when_enabled(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World 1').within(news_folder))

        portlet_config = {
            'Title': u'A News Portlet',
            'Link to RSS feed': True,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertEquals('Subscribe to the RSS feed',
                          browser.find('Subscribe to the RSS feed').text)

    @browsing
    def test_portlet_does_not_render_rss_link_when_disabled(self, browser):
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World 1').within(news_folder))

        portlet_config = {
            'Title': u'A News Portlet',
            'Link to RSS feed': False,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertIsNone(browser.find('Subscribe to the RSS feed'))

    @browsing
    def test_portlet_is_available_without_news_entries(self, browser):
        empty_folder = create(Builder('news folder')
                              .titled(u'Empty news folder'))

        portlet_config = {
            'Title': u'A News Portlet',
            'Limit to path': empty_folder,
            'Limit to current context': False,
            'Link to more news': True,
            'Always render the portlet': True,
        }
        self._add_portlet(browser, **portlet_config)

        self.assertIn('No recent news available.',
                      browser.css('.noRecentNews').text)
        self.assertEqual('More News', browser.find('More News').text)

    @browsing
    def test_portlet_is_not_available_without_news_entries(self, browser):
        """
        The same as `test_portlet_is_available_without_news_entries`
        but with 'Always render the portlet' set to False.

        """
        empty_folder = create(Builder('news folder')
                              .titled(u'Empty news folder'))

        portlet_config = {
            'Title': u'A News Portlet',
            'Limit to path': empty_folder,
            'Limit to current context': False,
            'Link to more news': True,
            'Always render the portlet': False,
        }
        self._add_portlet(browser, **portlet_config)
        self.assertIsNone(browser.find('More News'))

    @browsing
    def test_inherited_portlet_is_available(self, browser):
        """
        This test makes that a content page inherits the portlet from
        the plone root.
        """
        # Create a news portlet on root which will be inherited by the root's
        # child objects.
        form_values = {
            'Title': u'A News Portlet',
            'Always render the portlet': True,
            'Limit to current context': False,
            'Link to more news': True,
        }
        self._add_portlet(browser, **form_values)

        page = create(Builder('sl content page').titled(u'Content Page'))
        browser.login().visit(page)
        self.assertEqual('More News', browser.find('More News').text)

    @browsing
    def test_portlet_filters_by_quantity(self, browser):
        """
        This test makes sure that the portlet only renders news entries
        from the path configured in the portlet.
        """
        news_folder = create(Builder('news folder').titled(u'News Folder'))
        create(Builder('news').titled(u'Hello World 1').within(news_folder))
        create(Builder('news').titled(u'Hello World 2').within(news_folder))

        # Create the portlet on plone root.
        portlet_config = {
            'Title': 'A News Portlet',
            'Quantity': u'1',
        }
        self._add_portlet(browser, self.portal, **portlet_config)

        self.assertEqual(1, len(browser.css('.news-item')))
        self.assertIn('Hello World 1',
                      browser.css('.news-item .title').first.text)

    @browsing
    def test_news_portlet_listing_shows_more_items(self, browser):
        """
        This test makes sure the view behind the link "more news" on
        the portlet renders more news items.
        """
        # Create some content and the portlet
        page = create(Builder('sl content page').titled(u'Content Page'))
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .within(page))
        create(Builder('news').titled(u'Hello World').within(news_folder)
               .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))
        create(Builder('news').titled(u'Hello Again').within(news_folder)
               .having(news_date=datetime(2001, 1, 1, 15, 0, 0)))
        self._add_portlet(browser, page, **{'Title': 'A News Portlet',
                                            'Quantity': u'1',
                                            'Link to more news': True})
        browser.find('More News').click()
        self.assertEqual(
            ['Hello Again', 'Hello World'],
            browser.css('.news-listing .title').text
        )

    @browsing
    def test_news_portlet_shows_lead_image(self, browser):
        """
        This test makes sure that the news portlet renders the lead image
        if configured to do so.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        news_folder = create(Builder('news folder')
                             .titled(u'News Folder')
                             .within(page))
        news = create(Builder('news')
                      .titled(u'Hello World')
                      .within(news_folder))
        block = create(Builder('sl textblock')
                       .titled(u'Textblock with image')
                       .within(news)
                       .with_dummy_image())
        utils.create_page_state(news, block)

        self._add_portlet(browser,
                          self.portal,
                          **{'Title': 'A News Portlet',
                             'Limit to current context': False,
                             'Quantity': u'1',
                             'Show lead image': True})

        lead_image_css_selector = '.news-item img'

        browser.login().visit(page)
        self.assertEqual(
            'Textblock with image',
            browser.css(lead_image_css_selector).first.attrib['title']
        )

        # Configure the portlet not to show the lead image and make sure the
        # lead image is not rendered anymore.
        browser.find('Manage portlets').click()
        browser.find('News Portlet (A News Portlet)').click()
        browser.forms['form'].fill({'Show lead image': False}).save()

        browser.visit(page)
        self.assertEqual([], browser.css(lead_image_css_selector))

    @browsing
    def test_news_portlet_no_footer(self, browser):
        """
        This test makes sure that the portlet footer is absent when
        it does not have any content.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        news_folder = create(Builder('news folder').titled(u'News Folder')
                             .within(page))
        create(Builder('news').titled(u'Hello World').within(news_folder)
               .having(news_date=datetime(2000, 12, 31, 15, 0, 0)))
        create(Builder('news').titled(u'Hello Again').within(news_folder)
               .having(news_date=datetime(2001, 1, 1, 15, 0, 0)))
        self._add_portlet(browser, page, **{'Title': 'A News Portlet',
                                            'Always render the portlet': True,
                                            'Link to more news': False,
                                            'Link to RSS feed': False})

        self.assertEqual(
            [],
            browser.css('.news-portlet footer'),
            'A portlet footer has been found. But there should not be footer.'
        )

        # Now make sure the footer is there if it has content.
        browser.find('Manage portlets').click()
        browser.find('News Portlet (A News Portlet)').click()
        browser.forms['form'].fill({'Link to RSS feed': True}).save()

        browser.open(page)
        self.assertEqual(
            'Subscribe to the RSS feed',
            browser.css('.news-rss').first.text
        )
