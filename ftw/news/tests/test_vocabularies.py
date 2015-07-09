from ftw.builder import Builder
from ftw.builder import create
from ftw.news.testing import FTW_NEWS_FUNCTIONAL_TESTING
from plone.app.testing import login, TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import unittest2 as unittest


def terms_for(vocabulary_name, context):
    factory = getUtility(IVocabularyFactory,
                         name=vocabulary_name)
    return dict([(term.value, term.title)
                 for term in factory(context)])


class TestVocabularies(unittest.TestCase):

    layer = FTW_NEWS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_subject_vocabulary(self):
        create(Builder('news').titled(u'News 1')
               .having(subjects=['hans', 'maria']))
        create(Builder('news').titled(u'News 2')
               .having(subjects=['peter', 'maria']))

        login(self.portal, TEST_USER_NAME)

        self.assertEquals(
            {'hans': u'hans', 'peter': u'peter', 'maria': u'maria'},
            terms_for('ftw.news.vocabulary.subjects', self.portal))