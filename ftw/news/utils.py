from plone import api
import pkg_resources

IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'


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
    if user is None:
        return creator
    fullname = user.getProperty('fullname')
    return fullname or user.id


def can_view_about():
    """
    Returns a boolean indicating if the current is allowed to view about info.

    :rtype: bool
    """
    if IS_PLONE_5:
        allow_anonymous_view_about = api.portal.get_registry_record(
            'plone.allow_anon_views_about')
    else:
        site_props = api.portal.get_tool(
            name='portal_properties').site_properties
        allow_anonymous_view_about = site_props.getProperty(
            'allowAnonymousViewAbout', False)

    if not allow_anonymous_view_about and api.user.is_anonymous():
        return False
    return True


def crop_text(text, length):
    """
    Crops the given text to the given length.

    :param text: The text to be cropped
    :type text: str
    :param length: The maximum length of the cropped text
    :type length: int
    :return: The cropped text
    """
    plone_view = api.portal.get().restrictedTraverse('@@plone')
    return plone_view.cropText(text, length)


def make_utf8(item):
    if isinstance(item, unicode):
        return item.encode('utf-8')
    else:
        return item
