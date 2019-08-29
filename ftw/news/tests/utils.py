from ftw.simplelayout.interfaces import IPageConfiguration
from plone import api
from ftw.testing import IS_PLONE_5
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
import transaction


def create_page_state(obj, block):
    page_state = {
        "default": [
            {
                "cols": [
                    {
                        "blocks": [
                            {
                                "uid": IUUID(block)
                            }
                        ]
                    }
                ]
            },
        ]
    }
    page_config = IPageConfiguration(obj)
    page_config.store(page_state)
    transaction.commit()


def set_allow_anonymous_view_about(state):

    if IS_PLONE_5:
        api.portal.set_registry_record('plone.allow_anon_views_about', state)
    else:
        site_props = api.portal.get_tool(name='portal_properties').site_properties
        site_props.allowAnonymousViewAbout = state
    transaction.commit()


class LanguageSetter(object):

    def set_language_settings(self, default='en', supported=None,
                              use_combined=False, start_neutral=True):
        """
        Sets language settings regardeless if plone4.3 or plone5.1
        :param default: default site language
        :param supported: list of supported languages
        """
        # startNeutral is not used/available in plone 5.1 anymore

        if not supported:
            supported = ['en']

        if IS_PLONE_5:
            from Products.CMFPlone.interfaces import ILanguageSchema

            self.ltool = api.portal.get_tool('portal_languages')
            self.ltool.setDefaultLanguage(default)
            for lang in supported:
                self.ltool.addSupportedLanguage(lang)
            self.ltool.settings.use_combined_language_codes = False
            self.ltool.setLanguageCookie()
            registry = getUtility(IRegistry)
            language_settings = registry.forInterface(ILanguageSchema, prefix='plone')
            language_settings.use_content_negotiation = True
        else:
            self.ltool = self.portal.portal_languages
            self.ltool.manage_setLanguageSettings(
                default,
                supported,
                setUseCombinedLanguageCodes=use_combined,
                # Set this only for better testing ability
                setCookieEverywhere=True,
                startNeutral=start_neutral,
                setContentN=True)
        transaction.commit()
