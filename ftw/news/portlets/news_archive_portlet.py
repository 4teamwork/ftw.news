from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import monthname_msgid
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.news import _
from ftw.news.interfaces import INewsListingView
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.portlets import base
from plone.directives.form.form import SchemaAddForm
from plone.directives.form.form import SchemaEditForm
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletDataProvider
from z3c.form import button
from z3c.form import form as z3cform
from zope import schema
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implements


def zLocalizedTime(request, time, long_format=False):
    """Convert time to localized time
    """
    month_msgid = monthname_msgid(time.strftime('%m'))
    month = translate(month_msgid, domain='plonelocales',
                      context=request)

    return month.encode('utf-8')


class ArchiveSummary(object):

    def __init__(self, context, request, interfaces, date_field, view):
        self.context = context
        self.request = request
        self.interfaces = interfaces
        self.date_field = date_field
        self.view = view
        self.selected_year = None
        self.selected_month = None

    def __call__(self):
        self._set_selected_archive()

        entries = self._get_archive_entries()
        counter = self._count_entries(entries)

        result = []
        year_numbers = sorted(counter, reverse=True)

        for year_number in year_numbers:

            year = counter.get(year_number)
            months = year.get('months')
            month_numbers = sorted(months, reverse=True)
            month_list = []

            for month_number in month_numbers:
                date = '%s/%s/01' % (year_number, month_number)

                month_list.append(dict(
                    title=zLocalizedTime(self.request, DateTime(date)),
                    number=months.get(month_number),
                    url=self._get_archive_url(date),
                    mark=[self.selected_year, self.selected_month] == [
                        year_number, month_number]
                ))

            result.append(dict(
                title=year_number,
                number=year.get('num'),
                months=month_list,
                mark=self.selected_year == year_number
            ))

        return result

    def _set_selected_archive(self):
        selected_archive = self.request.get('archive')
        if selected_archive:
            self.selected_year = selected_archive.split('/')[0]
            self.selected_month = selected_archive.split('/')[1]

    def _get_archive_url(self, date):
        url = '{url}/{view}?archive={date}'.format(
            url=self.context.absolute_url(),
            view=self.view.__name__,
            date=date)

        portlet = self.request.get('portlet', None)
        manager = self.request.get('manager', None)
        if portlet:
            url += '&portlet={0}'.format(portlet)
        if manager:
            url += '&manager={0}'.format(manager)

        return url

    def _get_archive_entries(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = self._get_query()
        if 'start' in query:
            del query['start']
        return catalog(**query)

    def _get_query(self):
        return self.view.get_query()

    def _count_entries(self, entries):
        """Return a summary map like:

        {'2009': {
            'num': 6,
            'months': {
                '01': 4,
                '02': 2}
            }
        }
        """
        summary = {}

        for entry in entries:

            date = getattr(entry, self.date_field)
            if not date:
                continue

            year_name = date.strftime('%Y')
            month_name = date.strftime('%m')

            year_summary = summary.get(year_name, {})
            month_summary = year_summary.get('months', {})

            # Increase month
            month_summary.update(
                {month_name: month_summary.get(month_name, 0) + 1})
            year_summary.update({'months': month_summary})

            # Increase year
            year_summary.update({'num': year_summary.get('num', 0) + 1})
            summary.update({year_name: year_summary})

        return summary


class INewsArchivePortlet(IPortletDataProvider):
    """Archive portlet interface.
    """

    portlet_title = schema.TextLine(
        title=_(u'title', default=u'Title'),
        required=True,
        default=u'',
    )


class Assignment(base.Assignment):
    implements(INewsArchivePortlet)

    def __init__(self, portlet_title='', _portlet_title=''):
        self._portlet_title = portlet_title or _portlet_title

    @property
    def portlet_title(self):
        return (self._portlet_title if hasattr(self, '_portlet_title') else
                _(u'archive', default=u'Archive'))

    @portlet_title.setter
    def portlet_title(self, value):
        self._portlet_title = value

    @property
    def title(self):
        return u'News Archive Portlet ({0})'.format(self.portlet_title)


class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.data = data
        self.request = request
        self.view = view

    @property
    def available(self):
        """Show the portlet only if we're on a news listing view and
        there is some content to be displayed.
        """
        is_news_listing_view = INewsListingView.providedBy(self.view)
        return is_news_listing_view and bool(self.get_items())

    @memoize
    def get_items(self):
        """Returns an ordered list of summary info per month."""
        summary = ArchiveSummary(
            context=self.context,
            request=self.request,
            interfaces=['ftw.news.interfaces.INews'],
            date_field='start',
            view=self.view)()

        items = [{
            'title': year['title'],
            'count': year['number'],
            'class': 'year expanded' if year['mark'] else 'year',
            'months_expanded': 'months expanded' if year['mark'] else 'months',
            'months': [{
                'title': month['title'],
                'url': month['url'],
                'class': 'month highlight' if month['mark'] else 'month',
                'month': month['title'],
                'count': month['number'],
            } for month in year['months']],
        } for year in summary]
        return items

    render = ViewPageTemplateFile('templates/news_archive_portlet.pt')


class AddForm(SchemaAddForm):
    label = _(u'news_archive_portlet_add_form', default=u'Add News Archive Portlet')
    schema = INewsArchivePortlet

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
            portlet_title=data.get('portlet_title'),
        )


class EditForm(SchemaEditForm):
    label = _(u'news_archive_portlet_edit_form', default=u'Edit News Archive Portlet')
    schema = INewsArchivePortlet

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

    @button.buttonAndHandler(_(u'news_archive_portlet_edit_form_save',
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

    @button.buttonAndHandler(_(u'news_archive_portlet_edit_form_cancel',
                               default=u'Cancel'),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        return self.request.response.redirect(nextURL)

    updateActions = z3cform.EditForm.updateActions
