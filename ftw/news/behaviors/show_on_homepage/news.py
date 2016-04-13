from ftw.news import _
from plone.app.dexterity.behaviors import metadata
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides


class IShowOnHomepageSchema(form.Schema):

    read_permission(show_on_homepage='ftw.news.ShowNewsOnHomepage')
    write_permission(show_on_homepage='ftw.news.ShowNewsOnHomepage')
    show_on_homepage = schema.Bool(
        title=_(u'label_show_on_homepage', default=u'Show on home page'),
        description=_(
            u'description_show_on_homepage',
            default=u'If active, this news item may be shown on the homepage.'
        ),
        default=False,
        required=False,
    )

alsoProvides(IShowOnHomepageSchema, form.IFormFieldProvider)


class IShowOnHomepageBehaviorMarker(Interface):
    """
    Marker interface for the behavior.
    """


class IShowOnHomepage(Interface):
    """
    Marker interface to mark news to show up on home page. This is used
    in the factory of the behavior.
    """


class ShowOnHomepage(metadata.MetadataBase):

    @property
    def show_on_homepage(self):
        return IShowOnHomepage.providedBy(self.context)

    @show_on_homepage.setter
    def show_on_homepage(self, value):
        if value:
            alsoProvides(self.context, IShowOnHomepage)
        else:
            noLongerProvides(self.context, IShowOnHomepage)
