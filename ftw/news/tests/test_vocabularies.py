from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from ftw.news.tests.base import FunctionalTestCase
from plone.app.testing import login, TEST_USER_NAME
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


def terms_for(vocabulary_name, context):
    factory = getUtility(IVocabularyFactory,
                         name=vocabulary_name)
    return dict([(term.value, term.title)
                 for term in factory(context)])


class TestVocabularies(FunctionalTestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestVocabularies, self).setUp()
        self.grant('Contributor')

    def test_subject_vocabulary(self):
        create(Builder('news').titled(u'News 1')
               .having(subjects=['hans', u'mari\xe4']))
        create(Builder('news').titled(u'News 2')
               .having(subjects=['peter', u'mari\xe4']))

        login(self.portal, TEST_USER_NAME)
        self.assertEquals(
            {u'hans': u'hans', u'mari\xe4': u'mari\xe4', u'peter': u'peter'},
            terms_for('ftw.news.vocabulary.subjects', self.portal))
