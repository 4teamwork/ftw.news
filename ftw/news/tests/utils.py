from ftw.simplelayout.interfaces import IPageConfiguration
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
