from collective.taskqueue.testing import TASK_QUEUE_ZSERVER_FIXTURE
from collective.taskqueue.testing import ZSERVER_FIXTURE
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.simplelayout.tests import builders
from ftw.subsite.tests import builders
from ftw.testing import IS_PLONE_5
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.news.tests.builders
import ftw.referencewidget.tests.widgets


class FtwNewsLayer(PloneSandboxLayer):

    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.news:default')
        applyProfile(portal, 'ftw.subsite:default')
        applyProfile(portal, 'plone.restapi:default')
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


FTW_NEWS_FIXTURE = FtwNewsLayer()

FTW_NEWS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_NEWS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.news:functional")


class MopageTriggerLayer(FtwNewsLayer):

    def setUpZope(self, app, configurationContext):
        super(MopageTriggerLayer, self).setUpZope(app, configurationContext)
        xmlconfig.string(
            '''
            <configure xmlns="http://namespaces.zope.org/zope"
                       xmlns:browser="http://namespaces.zope.org/browser">

                <browser:page
                    for="*"
                    name="mopage-stub"
                    class="ftw.news.tests.test_mopage_trigger.MopageAPIStub"
                    permission="zope2.View"
                    />

            </configure>''',
            context=configurationContext)


MOPAGE_TRIGGER_FIXTURE = MopageTriggerLayer()


MOPAGE_TRIGGER_FUNCTIONAL = FunctionalTesting(
    bases=(ZSERVER_FIXTURE,
           TASK_QUEUE_ZSERVER_FIXTURE,
           MOPAGE_TRIGGER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.news:functional:taskqueue")
