from hashlib import md5
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class SubjectVocabulary(SimpleVocabulary):

    def __init__(self, terms, *interfaces):
        terms = self.get_terms()
        super(SubjectVocabulary, self).__init__(terms, *interfaces)

    def search(self, query_string):
        return [v for v in self if query_string.lower() in v.value.lower()]

    def get_terms(self):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog', None)
        normalizer = queryUtility(IIDNormalizer)
        terms = []

        for term in catalog.uniqueValuesFor('Subject'):
            # Just the normalized term is not enough for an unique token.
            # The unique values are case sensitive. After normalizing the
            # term, we get id's in lower-case. That means, we lose the
            # unique value after normalizing if we get values like: "Bond"
            # and "bonD". Adding an md5 hash to the normalized term, we
            # prevent double tokens and the token is still readable.
            token = '{0}-{1}'.format(md5(term).hexdigest(),
                                     normalizer.normalize(term))
            terms.append(SimpleTerm(value=term.decode('utf8'),
                                    token=token.decode('utf8'),
                                    title=term.decode('utf8')))
        return terms

directlyProvides(SubjectVocabulary, IVocabularyFactory)
