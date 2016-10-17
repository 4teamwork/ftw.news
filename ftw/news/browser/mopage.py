from DateTime import DateTime
from ftw.news.behaviors.mopage import IMopageModificationDate
from htmlentitydefs import name2codepoint as n2cp
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

    if isinstance(text, str):
        text = text.decode('utf-8')
    if len(text) > length:
        text = text[:length - 5] + ' ...'

    return text


def decode_entities(text):
    """
    Decodes html entities and xml entities.
    """
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")

    def substitute_entity(match):
        ent = match.group(2)
        if match.group(1) == "#":
            return unichr(int(ent))

        else:
            cp = n2cp.get(ent)
            if cp:
                return unichr(cp)
            else:
                return match.group()

    return entity_re.subn(substitute_entity, text)[0]


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

        modified_date = IMopageModificationDate(obj).get_date()
        return {'title': crop(100, brain.Title),
                'news_date': self.normalize_date(brain.start),
                'expires': self.normalize_date(brain.expires),
                'modified_date': self.normalize_date(modified_date),
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

    def cleanup_body_html(self, html):
        """We have HTML with simplelayout structure, but this is too noisy
        for the import.
        We therefore convert the HTML to text and back to HTML.
        We also need to make sure that the result is less than 10000 long.
        """

        doc = lxml.html.fromstring(html)
        map(remove_node, doc.xpath(
            '//*[contains(concat(" ", normalize-space(@class), " "), '
            '" hiddenStructure ")]'))
        html = lxml.etree.tostring(doc, pretty_print=True)

        portal_transforms = getToolByName(self.context, 'portal_transforms')
        text = decode_entities(portal_transforms.convertToData(
            'text/x-web-intelligent',
            html,
            mimetype='text/html').strip())

        # body limit is 10000.
        # We have text here, but will convert it to HTML, so it will be larger
        # and we need to crop more to compensate.
        for attempt in range(100):
            text = crop(10000 - (len(text) * 0.1), text)
            html = portal_transforms.convertToData(
                'text/html',
                text,
                mimetype='text/x-web-intelligent').strip()

            if len(html) < 10000:
                return u'<![CDATA[' + html + u']]>'

        return u'<![CDATA[cropping error]]>'

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
