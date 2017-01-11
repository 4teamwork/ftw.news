from ftw.news import _
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class INewsExternalUrl(form.Schema):

    write_permission(external_url='ftw.news.EditNewsExternalUrl')
    external_url = schema.URI(
        title=_(u'label_news_external_url',
                default=u'External link for mobile app'),
        default=None,
        required=False,
    )
