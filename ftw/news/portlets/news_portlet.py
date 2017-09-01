from Acquisition import aq_parent, aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.news import _
from ftw.news import utils
from ftw.news.contents.common import INewsListingBaseSchema
from ftw.news.interfaces import INewsFolder
from plone import api
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.portlets import base
from plone.directives.form.form import SchemaAddForm, SchemaEditForm
from plone.portlets.interfaces import IPortletDataProvider
from z3c.form import button
from z3c.form import form as z3cform
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements


class INewsPortlet(INewsListingBaseSchema, IPortletDataProvider):

    always_render_portlet = schema.Bool(
        title=_(u'news_portlet_always_render_portlet_label',
                default=u'Always render the portlet'),
        description=_(u'news_portlet_always_render_portlet_description',
                      default=u'Render the portlet even if there are no news '
                              u'entries.'),
        default=False,
    )


class AddForm(SchemaAddForm):
    label = _(u'news_portlet_add_form_label', default=u'Add News Portlet')
    description = _(u'news_portlet_add_form_description',
                    default=u'This portlet displays news items')

    schema = INewsPortlet

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

    def add(self, object_):
        ob = self.context.add(object_)
        self._finishedAdd = True
        return ob

    def create(self, data):
        return Assignment(
            news_listing_config_title=data.get('news_listing_config_title'),
            current_context=data.get('current_context', True),
            quantity=data.get('quantity', 5),
            filter_by_path=data.get('filter_by_path', []),
            subjects=data.get('subjects', []),
            show_description=data.get('show_description', False),
            description_length=data.get('description_length', 50),
            maximum_age=data.get('maximum_age', 0),
            show_more_news_link=data.get('show_more_news_link', 0),
            show_rss_link=data.get('show_rss_link', 0),
            always_render_portlet=data.get('always_render_portlet', False),
            show_lead_image=data.get('show_lead_image', False),
        )


class Assignment(base.Assignment):
    implements(INewsPortlet)

    def __init__(self, news_listing_config_title='News', current_context=True,
                 quantity=5, filter_by_path=None, subjects=None,
                 show_description=False, description_length=50, maximum_age=0,
                 show_more_news_link=False, show_rss_link=False,
                 always_render_portlet=False, show_lead_image=False):
        self.news_listing_config_title = news_listing_config_title
        self.current_context = current_context
        self.quantity = quantity
        self.filter_by_path = filter_by_path or []
        self.subjects = subjects or []
        self.show_description = show_description
        self.description_length = description_length
        self.maximum_age = maximum_age
        self.show_more_news_link = show_more_news_link
        self.show_rss_link = show_rss_link
        self.always_render_portlet = always_render_portlet
        self.show_lead_image = show_lead_image

    @property
    def title(self):
        """This property is used to display the title of the portlet in the
        "manage portlets" screen. The user defined title of the portlet
        instance is appended to the default title which is useful if there
        is more than one news portlet.
        """
        return u'News Portlet ({0})'.format(self.news_listing_config_title)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/news_portlet.pt')

    @property
    def available(self):
        if getattr(self.data, 'always_render_portlet', False):
            return True

        if INewsFolder.providedBy(self.data):
            return False

        return bool(self.get_news())

    def get_query(self, all_news):
        query = {'object_provides': 'ftw.news.interfaces.INews'}

        if self.data.current_context:
            context_state = self.context.restrictedTraverse(
                'plone_context_state')
            path = '/'.join(context_state.canonical_object().getPhysicalPath())
            query['path'] = {'query': path}
        elif self.data.filter_by_path:
            cat_path = []
            for item in self.data.filter_by_path:
                if item.to_object:
                    cat_path.append('/'.join(item.to_object.getPhysicalPath()))
            query['path'] = {'query': cat_path}

        if self.data.subjects:
            query['Subject'] = map(utils.make_utf8, self.data.subjects)

        if self.data.maximum_age > 0 and not all_news:
            date = DateTime() - self.data.maximum_age
            query['start'] = {'query': date, 'range': 'min'}

        query['sort_on'] = 'start'
        query['sort_order'] = 'descending'

        # Show inactive news if the current user is allowed to add news items on the
        # context where this portlet is assigned to. We must only render the inactive news
        # if the portlet renders news items from the current context (in order not to
        # allow the user to view news items he is not allowed to see).
        if self.data.current_context \
                and not self.data.filter_by_path \
                and api.user.has_permission('ftw.news: Add News', obj=self.context):
            query['show_inactive'] = True

        return query

    def get_news(self, all_news=False):
        """
        Return a list of catalog brains.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(self.get_query(all_news))

        if not all_news and self.data.quantity:
            results = results[:self.data.quantity]

        return results

    def get_items(self, all_news=False):
        """
        Returns a list of dict to be used in the template.
        """
        news = self.get_news(all_news)
        items = [self.get_item_dict(brain) for brain in news]
        return items

    def get_item_dict(self, brain):
        obj = brain.getObject()

        description = ''
        if self.data.show_description:
            description = brain.Description
        if self.data.description_length:
            description = utils.crop_text(description,
                                          self.data.description_length)
        image_tag = ''
        if self.data.show_lead_image:
            image_tag = obj.restrictedTraverse('@@leadimage')

        item = {
            'title': brain.Title,
            'description': description,
            'url': brain.getURL(),
            'news_date': self.format_date(brain),
            'author': utils.get_creator(obj) if utils.can_view_about() else '',
            'image_tag': image_tag,
        }
        return item

    def format_date(self, brain):
        return self.context.toLocalizedTime(brain.start, long_format=False)

    def show_rss_link(self):
        return getattr(self.data, 'show_rss_link', False)

    def more_news_url(self):
        if self.data.show_more_news_link:
            params = 'portlet={0}&manager={1}'.format(
                self.data.__name__,
                self.manager.__name__)

            return '/'.join((self.context.absolute_url(),
                             '@@news_portlet_listing?{0}'.format(params)))
        return ''


class EditForm(SchemaEditForm):
    label = _(u'news_portlet_edit_form_label', default=u'Edit News Portlet')
    description = _(u'news_portlet_edit_form_description',
                    default=u'This portlet displays news items')

    schema = INewsPortlet

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

    updateActions = z3cform.EditForm.updateActions
