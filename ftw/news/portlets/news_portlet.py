from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from ftw.news import _
from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.portlets import base
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import form, button, field, interfaces
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements, invariant, Invalid


class INewsPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u'news_portlet_title_label', default=u'Title'),
        description=u'',
        required=True,
        default=u'')

    path = schema.List(
        title=_(u'news_portlet_filter_path_label', default=u'Limit to path'),
        description=_(u'news_portlet_filter_path_description',
                      default=u'Only show news items from a specific path.'),
        value_type=schema.Choice(
            source=PathSourceBinder(
                navigation_tree_query={'is_folderish': True},
                is_folderish=True),
        ),
        required=False,
    )

    current_context = schema.Bool(
        title=_(u'news_portlet_filter_current_context_label',
                default=u'Limit to current context'),
        description=_(u'news_portlet_filter_current_context_description',
                      default=u'Only show news items from the current '
                              u'context.'),
        default=True,
    )

    quantity = schema.Int(
        title=_(u'news_portlet_quantity_label', default=u'Quantity'),
        description=_(u'news_portlet_quantity_description',
                      default=u'The number of news entries to be '
                              u'shown at most.'),
        default=5,
    )

    # TODO: Find a better widget than the one we're using (defined in the forms below).
    subjects = schema.List(
        title=_(u'news_portlet_subjects_label',
                default=u'Filter by subject'),
        description=_(u'news_portlet_subjects_description',
                      default=u'Only news with the selected subjects will '
                              u'be shown.'),
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.Keywords'),
        required=False,
    )

    show_description = schema.Bool(
        title=_(u'news_portlet_show_description_label',
                default=u'Show the description of the news item'),
        default=True
    )

    description_length = schema.Int(
        title=_(u'news_portlet_description_length_label',
                default=u'Length of the description'),
        description=_(u'news_portlet_description_length_description',
                      default=u'The maximum length of the news item\'s '
                              u'description. Longer descriptions will be '
                              u'cropped.'),
        default=50,
    )

    maximum_age = schema.Int(
        title=_(u'news_portlet_maximum_age_label',
                default=u'Maximum age (days)'),
        description=_(u'news_portlet_maximum_age_description',
                      default=u'Only news younger than this value will be '
                              u'rendered. Enter 0 for no limitation.'),
        default=0,
        required=True,
    )

    show_more_news_link = schema.Bool(
        title=_(u'news_portlet_show_more_news_link_label',
                default=u'Link to more news'),
        description=_(u'news_portlet_show_more_news_link_description',
                      default=u'Render a link to a page which renders more '
                              u'news (only if there is at least one news '
                              u'item.'),
        default=False,
    )

    show_rss_link = schema.Bool(
        title=_(u'news_portlet_show_rss_link_label',
                default=u'Link to RSS feed'),
        description=_(u'news_portlet_show_rss_link_description',
                      default=u'Render a link to the RSS feed of the news.'),
        default=False,
    )

    always_render_portlet = schema.Bool(
        title=_(u'news_portlet_always_render_portlet_label',
                default=u'Always render the portlet'),
        description=_(u'news_portlet_always_render_portlet_description',
                      default=u'Render the portlet even if there are no news '
                              u'entries.'),
        default=False,
    )

    @invariant
    def is_either_path_or_context(obj):
        """Checks if not both path and current context are defined.
        """
        if obj.current_context and obj.path:
            raise Invalid(_(
                u'news_portlet_current_context_and_path_error',
                default=u'You can not filter by path and current context '
                        u'at the same time.')
            )


class AddForm(form.AddForm):
    implements(IPortletAddForm)
    label = _(u'news_portlet_add_form_label', default=u'Add News Portlet')
    description = _(u'news_portlet_add_form_description',
                    default=u'This portlet displays news items')

    fields = field.Fields(INewsPortlet)
    fields['subjects'].widgetFactory = CheckBoxFieldWidget

    def __init__(self, context, request):
        super(AddForm, self).__init__(context, request)
        self.status = None
        self._finishedAdd = None

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(AddForm, self).__call__()

    def nextURL(self):
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        url = str(getMultiAdapter((context, self.request),
                                  name=u'absolute_url'))
        return url + '/@@manage-portlets'

    @button.buttonAndHandler(_(u'news_portlet_add_form_save_label',
                               default=u'Save'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(_(u'news_portlet_add_form_cancel_label',
                               default=u'Cancel'),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        return self.request.response.redirect(nextURL)

    def add(self, object_):
        ob = self.context.add(object_)
        self._finishedAdd = True
        return ob

    def updateWidgets(self):
        self.fields['path'].widgetFactory = MultiContentTreeFieldWidget
        super(AddForm, self).updateWidgets()

    def create(self, data):
        return Assignment(
            portlet_title=data.get('portlet_title'),
            current_context=data.get('current_context', True),
            quantity=data.get('quantity', 5),
            path=data.get('path', []),
            subjects=data.get('subjects', []),
            show_description=data.get('show_description', False),
            description_length=data.get('description_length', 50),
            maximum_age=data.get('maximum_age', 0),
            show_more_news_link=data.get('show_more_news_link', 0),
            show_rss_link=data.get('show_rss_link', 0),
            always_render_portlet=data.get('always_render_portlet', False)
        )


class Assignment(base.Assignment):
    implements(INewsPortlet)

    def __init__(self, portlet_title='News', current_context=True, quantity=5,
                 path=None, subjects=None, show_description=False,
                 description_length=50, maximum_age=0,
                 show_more_news_link=False, show_rss_link=False,
                 always_render_portlet=False):
        self.portlet_title = portlet_title
        self.current_context = current_context
        self.quantity = quantity
        self.path = path or []
        self.subjects = subjects or []
        self.show_description = show_description
        self.description_length = description_length
        self.maximum_age = maximum_age
        self.show_more_news_link = show_more_news_link
        self.show_rss_link = show_rss_link
        self.always_render_portlet = always_render_portlet

    @property
    def title(self):
        """This property is used to display the title of the portlet in the
        "manage portlets" screen. The user defined title of the portlet
        instance is appended to the default title which is useful if there
        is more than one news portlet.
        """
        return u'News Portlet ({0})'.format(self.portlet_title)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('news_portlet.pt')

    @property
    def available(self):
        if getattr(self.data, 'always_render_portlet', False):
            return True

        if self.context.portal_type == 'ftw.news.NewsFolder':
            return False

        if self.show_more_news_link():
            has_news = self.get_news(all_news=True)
        else:
            has_news = self.get_news()
        return has_news

    def get_news(self, all_news=False):
        catalog = getToolByName(self.context, 'portal_catalog')
        url_tool = getToolByName(self.context, 'portal_url')
        portal_path = url_tool.getPortalPath()
        query = {'object_provides': 'ftw.news.interfaces.INews'}

        if self.data.current_context:
            path = '/'.join(self.context.getPhysicalPath())
            query['path'] = {'query': path}

        else:
            if self.data.path:
                cat_path = []
                for item in self.data.path:
                    cat_path.append('/'.join([portal_path, item]))
                query['path'] = {'query': cat_path}

        if self.data.subjects:
            query['Subject'] = self.data.subjects

        if self.data.maximum_age > 0 and not all_news:
            date = DateTime() - self.data.maximum_age
            query['effective'] = {'query': date, 'range': 'min'}

        query['sort_on'] = 'effective'
        query['sort_order'] = 'descending'
        results = catalog.searchResults(query)

        if not all_news and self.data.quantity:
            results = results[:self.data.quantity]

        return results

    def crop_desc(self, description):
        ploneview = self.context.restrictedTraverse('@@plone')
        return ploneview.cropText(description, self.data.description_length)

    def show_more_news_link(self):
        return self.data.show_more_news_link

    def show_rss_link(self):
        return getattr(self.data, 'show_rss_link', False)

    def more_news_url(self):
        params = 'portlet={0}&manager={1}'.format(
            self.data.__name__,
            self.manager.__name__)

        return '/'.join((self.context.absolute_url(),
                         '@@news_portlet_listing?{0}'.format(params)))


class EditForm(form.EditForm):
    implements(IPortletEditForm)
    label = _(u'news_portlet_edit_form_label', default=u'Edit News Portlet')
    description = _(u'news_portlet_edit_form_description',
                    default=u'This portlet displays news items')

    fields = field.Fields(INewsPortlet)
    fields['subjects'].widgetFactory = CheckBoxFieldWidget

    def __init__(self, context, request):
        super(EditForm, self).__init__(context, request)
        self.status = None
        self._finishedAdd = None

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(EditForm, self).__call__()

    def nextURL(self):
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        url = str(getMultiAdapter((context, self.request),
                                  name=u'absolute_url'))
        return url + '/@@manage-portlets'

    @button.buttonAndHandler(_(u'news_portlet_edit_form_save_label',
                               default=u'Save'),
                             name='apply')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = 'Changes saved'
        else:
            self.status = 'No changes'

        nextURL = self.nextURL()
        return self.request.response.redirect(nextURL)

    @button.buttonAndHandler(_(u'news_portlet_edit_form_cancel_label',
                               default=u'Cancel'),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        return self.request.response.redirect(nextURL)

    def updateWidgets(self):
        self.fields['path'].widgetFactory = MultiContentTreeFieldWidget
        super(EditForm, self).updateWidgets()
