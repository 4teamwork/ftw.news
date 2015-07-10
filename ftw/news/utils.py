from plone import api


def get_creator(item):
    """
    Returns the full name of the given item.

    :param item: A brain or an object
    :return: The fullname of the creator of the item
    :rtype: str
    """
    creator = getattr(item, 'Creator', '')
    username = creator() if callable(creator) else creator
    user = api.user.get(username=username)
    fullname = user.getProperty('fullname')
    return fullname or user.id


def can_view_about():
    """
    Returns a boolean indicating if the current is allowed to view about info.

    :rtype: bool
    """
    site_props = api.portal.get_tool(name='portal_properties').site_properties
    allow_anonymous_view_about = site_props.getProperty(
        'allowAnonymousViewAbout', False)

    if not allow_anonymous_view_about and api.user.is_anonymous():
        return False
    return True
