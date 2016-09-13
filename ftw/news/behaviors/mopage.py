from Acquisition import aq_chain
from ftw.news import _
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.directives.form import fieldset
from plone.directives.form import IFormFieldProvider
from plone.directives.form import Schema
from Products.Five.browser import BrowserView
from zope import schema
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import Interface
import requests
import urllib
import urlparse


class IPublisherMopageTrigger(Schema):

    fieldset('mopage',
             label=_(u'Mopage'),
             fields=['mopage_enabled',
                     'mopage_trigger_url',
                     'mopage_data_endpoint_url'])

    read_permission(mopage_enabled='ftw.news.ConfigureMopageTrigger')
    write_permission(mopage_enabled='ftw.news.ConfigureMopageTrigger')
    mopage_enabled = schema.Bool(
        title=_(u'label_trigger_enabled',
                default=u'Mopage trigger enabled'),
        default=False,
        required=False,
    )

    read_permission(mopage_trigger_url='ftw.news.ConfigureMopageTrigger')
    write_permission(mopage_trigger_url='ftw.news.ConfigureMopageTrigger')
    mopage_trigger_url = schema.URI(
        title=_(u'label_mopage_trigger_url',
                default=u'Mopage trigger URL'),
        description=_(
            u'description_mopage_trigger_url',
            default=u'Contains the mopage URL to the trigger endpoint.'
            u' This is only the base URL, it does not contain the endpoint URL'
            u' from which the mopage server retrieves the news.'
            u' Example: https://un:pw@xml.mopage.ch/infoservice/xml.php'
        ),
        default=None,
        required=False,
    )

    read_permission(mopage_data_endpoint_url='ftw.news.ConfigureMopageTrigger')
    write_permission(mopage_data_endpoint_url='ftw.news.ConfigureMopageTrigger')
    mopage_data_endpoint_url = schema.URI(
        title=_(u'label_mopage_data_endpoint_url',
                default=u'Mopage data endpoint URL (Plone)'),
        description=_(
            u'description_mopage_data_endpoint_url',
            default=u'The mopage data endpoint URL points to the'
            u' "mopage.news.xml" view somewhere on the public visible '
            u' Plone page. It must also contain the params "partnerid"'
            u' and "importid".'
            u' Example: https://mypage.ch/news/'
            u'mopage.news.xml?partnerid=3&importid=6'
        ),
        default=None,
        required=False,
    )


alsoProvides(IPublisherMopageTrigger, IFormFieldProvider)


class IPublisherMopageTriggerSupport(Interface):
    """Marker interface for news folders which support IPublisherMopageTrigger.
    """


class PublisherMopageTrigger(MetadataBase):
    """Behavior adapter for IPublisherMopageTrigger.
    The storage is the adapted context.
    """

    mopage_enabled = DCFieldProperty(
        IPublisherMopageTrigger['mopage_enabled'])
    mopage_trigger_url = DCFieldProperty(
        IPublisherMopageTrigger['mopage_trigger_url'])
    mopage_data_endpoint_url = DCFieldProperty(
        IPublisherMopageTrigger['mopage_data_endpoint_url'])

    def is_enabled(self):
        return self.mopage_enabled \
            and self.mopage_trigger_url \
            and self.mopage_data_endpoint_url

    def build_trigger_url(self):
        if not self.is_enabled():
            return None

        parts = list(urlparse.urlparse(self.mopage_trigger_url))
        parts[5] = ''  # drop anchor
        parts[4] = urllib.urlencode({'url': self.mopage_data_endpoint_url})
        return urlparse.urlunparse(parts)


def trigger_mopage_refresh(news, event):
    triggers = filter(None,
                      map(lambda obj: IPublisherMopageTrigger(obj, None),
                          aq_chain(news)))
    if not triggers or not triggers[0].is_enabled():
        return

    from collective.taskqueue import taskqueue

    trigger_url = triggers[0].build_trigger_url()
    callback_path = '/'.join(getSite().getPhysicalPath()
                             + ('taskqueue_news_trigger_mopage_refresh',))
    taskqueue.add(callback_path, params={'target': trigger_url})


class TriggerMopageRefreshTaskQueueWorker(BrowserView):

    def __call__(self):
        requests.get(self.request.form['target']).raise_for_status()
