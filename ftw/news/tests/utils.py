from ftw.simplelayout.interfaces import IPageConfiguration
from plone import api
from plone.uuid.interfaces import IUUID
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
    site_props = api.portal.get_tool(name='portal_properties').site_properties
    site_props.allowAnonymousViewAbout = state
    transaction.commit()
