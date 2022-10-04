from ftw.news.interfaces import INewsListingBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.restapi.content import PersistenceDecoder
from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
import json


@implementer(ISerializeToJson)
@adapter(INewsListingBlock, Interface)
class SerializeNewsListingBlockToJson(SerializeToJson):
    def __call__(self, version=None, include_items=False):
        result = super(SerializeNewsListingBlockToJson, self).__call__(version=version)

        include_items = self.request.form.get("include_items", include_items)
        include_items = boolean_value(include_items)
        if include_items:
            catalog = api.portal.get_tool('portal_catalog')

            brains = catalog.searchResults(**self.get_query())

            original = self.request.get('ACTUAL_URL')
            self.request['ACTUAL_URL'] = self.context.absolute_url()
            batch = HypermediaBatch(self.request, brains)

            if not self.request.form.get("fullobjects"):
                result["@id"] = batch.canonical_url
            result["items_total"] = batch.items_total
            if batch.links:
                result["batching"] = batch.links

            if "fullobjects" in list(self.request.form):
                result["items"] = [
                    getMultiAdapter(
                        (brain.getObject(), self.request), ISerializeToJson
                    )()
                    for brain in batch
                ]
            else:
                result["items"] = [
                    getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
                    for brain in batch
                ]

            self.request['ACTUAL_URL'] = original

        result['block-configuration'] = json.loads(json.dumps(
            IBlockConfiguration(self.context).load(),
            cls=PersistenceDecoder)
        )

        return result

    def get_query(self):
        return self.context.restrictedTraverse('@@news_listing').get_query()
