from DateTime import DateTime
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
import lxml.html
import math
import re
import urllib
import urlparse


def normalize_whitespace(text, replacement=' '):
    text = re.sub(r'^\s+', replacement, text)
    text = re.sub(r'\s+$', replacement, text)
    return text


def normalize_join(*parts):
    return normalize_whitespace(''.join([part or '' for part in parts]))


def remove_node(node):
    parent = node.getparent()
    if parent is None:
        return

    position = parent.index(node)

    if position == 0:
        parent.text = normalize_join(parent.text, node.tail)
    else:
        sibling = parent[position - 1]
        sibling.tail = normalize_join(sibling.tail, node.tail)

    parent.remove(node)


def crop(length, text):
    if not text:
        return text

    text = text.decode('utf-8')
    if len(text) > length:
        text = text[:length - 5] + ' ...'

    return text


class MopageNews(BrowserView):
    """Documentation: http://doc.mopage.ch/ext/XML_Schnittstelle/2_XML_Aufbau
    """

    def __call__(self):
        self.request.RESPONSE.setHeader('Cache-Control', 'no-store')
        self.request.RESPONSE.setHeader('Content-Type',
                                        'text/xml;charset=utf-8')
        return super(MopageNews, self).__call__()

    def import_node_attributes(self):
        attrs = {'export_time': self.normalize_date(DateTime())}
        for name in ('partner', 'partnerid', 'passwort', 'importid',
                     'vaterobjekt'):
            attrs[name] = self.request.form.get(name, None)
        return attrs

    def items(self):
        brains = self.apply_pagination(self.get_brains())
        return map(self.brain_to_item, brains)

    def get_brains(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(self.get_query())

    def apply_pagination(self, brains):
        per_page = self.get_int_param_from_request('per_page', 100)
        page = self.get_int_param_from_request('page', 1)
        last = page * per_page
        first = last - per_page
        batch = brains[first:last]

        links = []
        if page > 1:
            links.append(self.build_pagination_link('first', page=1))
            links.append(self.build_pagination_link('prev', page=page - 1))

        if len(brains) > last:
            links.append(self.build_pagination_link('next',
                                                    page=int(page + 1)))
            links.append(self.build_pagination_link(
                'last', page=int(math.ceil(len(brains) / float(per_page)))))

        if links:
            self.request.RESPONSE.setHeader('Link', ','.join(links))

        return batch

    def get_query(self):
        return {
            'object_provides': 'ftw.news.interfaces.INews',
            'sort_on': 'start',
            'sort_order': 'reverse',
            'path': '/'.join(self.context.getPhysicalPath())}

    def brain_to_item(self, brain):
        obj = brain.getObject()
        image_url = self.get_lead_image_url(obj)

        if image_url and len(image_url) > 255:
            # sorry, not supported.
            image_url = None

        textlead = crop(100, obj.Description() or '')
        if textlead:
            textlead = u'<![CDATA[{}]]>'.format(textlead)

        subjects = getattr(ICategorization(obj, None), 'subjects', ())

        return {'title': crop(100, brain.Title),
                'news_date': self.normalize_date(brain.start),
                'expires': self.normalize_date(brain.expires),
                'modified_date': self.normalize_date(brain.modified),
                'uid': IUUID(obj),
                'url': brain.getURL(),
                'textlead': textlead,
                'image_url': image_url,
                'subjects': map(lambda subject: crop(100, subject), subjects),
                'obj': obj}

    def normalize_date(self, date):
        if not date:
            return ''

        if DateTime(date) > DateTime(2100, 1, 1):
            return None

        return date.strftime('%Y-%m-%d %H:%M:%S')

    def html_to_text(self, html):
        doc = lxml.html.fromstring(html)
        map(remove_node, doc.xpath(
            '//*[contains(concat(" ", normalize-space(@class), " "), '
            '" hiddenStructure ")]'))
        html = lxml.etree.tostring(doc, pretty_print=True)

        portal_transforms = getToolByName(self.context, 'portal_transforms')
        data = portal_transforms.convertTo('text/x-web-intelligent',
                                           html,
                                           mimetype='text/html')
        text = data.getData().strip()
        text = crop(10000, text)
        return u'<![CDATA[' + text + u']]>'

    def get_lead_image_url(self, news):
        scale = news.restrictedTraverse('@@leadimage').get_scale()
        return scale and scale.url or None

    def get_int_param_from_request(self, name, default):
        value = int(self.request.get(name, default))
        if value < 1:
            raise BadRequest('Invalid "{}" parameter value.'.format(name))
        return value

    def build_pagination_link(self, rel, **kwargs):
        params = self.request.form.copy()
        params.update(kwargs)
        parts = list(urlparse.urlparse(self.request.ACTUAL_URL))
        parts[4] = urllib.urlencode(params)
        url = urlparse.urlunparse(parts)
        return '<{}>; rel="{}"'.format(url, rel)
