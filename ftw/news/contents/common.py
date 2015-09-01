from ftw.news import _
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from z3c.relationfield import RelationChoice
from zope import schema
from zope.interface import invariant, Invalid


class INewsListingBaseSchema(form.Schema):
    """
    This schema is used in multiple places to store values which will then
    be used to determine which news items to render.
    """
    news_listing_config_title = schema.TextLine(
        title=_(u'news_listing_config_title_label', default=u'Title'),
        description=u'',
        required=True,
        default=u'',
    )

    form.widget(filter_by_path=MultiContentTreeFieldWidget)
    filter_by_path = schema.List(
        title=_(u'news_listing_config_filter_path_label',
                default=u'Limit to path'),
        description=_(u'news_listing_config_filter_path_description',
                      default=u'Only show news items from a specific path.'),
        value_type=RelationChoice(
            source=PathSourceBinder(
                navigation_tree_query={'is_folderish': True},
                is_folderish=True
            ),
        ),
        required=False,
        missing_value=[],
    )

    current_context = schema.Bool(
        title=_(u'news_listing_config_filter_current_context_label',
                default=u'Limit to current context'),
        description=_(
            u'news_listing_config_filter_current_context_description',
            default=u'Only show news items from the current context.'),
        default=True,
    )

    quantity = schema.Int(
        title=_(u'news_listing_config_quantity_label', default=u'Quantity'),
        description=_(u'news_listing_config_quantity_description',
                      default=u'The number of news entries to be '
                              u'shown at most. Enter 0 for no limitation.'),
        default=5,
    )

    # MAYBE: Find a better widget.
    form.widget(subjects=AutocompleteMultiFieldWidget)
    subjects = schema.List(
        title=_(u'news_listing_config_subjects_label',
                default=u'Filter by subject'),
        description=_(u'news_listing_config_subjects_description',
                      default=u'Only news with the selected subjects will '
                              u'be shown.'),
        value_type=schema.Choice(vocabulary='ftw.news.vocabulary.subjects'),
        required=False,
        missing_value=[],
    )

    show_description = schema.Bool(
        title=_(u'news_listing_config_show_description_label',
                default=u'Show the description of the news item'),
        default=True,
    )

    description_length = schema.Int(
        title=_(u'news_listing_config_description_length_label',
                default=u'Length of the description'),
        description=_(u'news_listing_config_description_length_description',
                      default=u'The maximum length of the news item\'s '
                              u'description. Longer descriptions will be '
                              u'cropped. Enter 0 for no limitation.'),
        default=50,
    )

    maximum_age = schema.Int(
        title=_(u'news_listing_config_maximum_age_label',
                default=u'Maximum age (days)'),
        description=_(u'news_listing_config_maximum_age_description',
                      default=u'Only news younger than this value will be '
                              u'rendered. Enter 0 for no limitation.'),
        default=0,
        required=True,
    )

    show_more_news_link = schema.Bool(
        title=_(u'news_listing_config_show_more_news_link_label',
                default=u'Link to more news'),
        description=_(u'news_listing_config_show_more_news_link_description',
                      default=u'Render a link to a page which renders more '
                              u'news (only if there is at least one news '
                              u'item.'),
        default=False,
    )

    show_rss_link = schema.Bool(
        title=_(u'news_listing_config_show_rss_link_label',
                default=u'Link to RSS feed'),
        description=_(u'news_listing_config_show_rss_link_description',
                      default=u'Render a link to the RSS feed of the news.'),
        default=False,
    )

    show_lead_image = schema.Bool(
        title=_(u'news_listing_config_show_lead_image_label',
                default=u'Show lead image'),
        description=_(u'news_listing_config_show_lead_image_description',
                      default=u'Renders a lead image (taken from the item\'s '
                              u'first text block having an image.)'),
        default=False,
    )

    @invariant
    def is_either_path_or_context(obj):
        """Checks if not both path and current context are defined.
        """
        if obj.current_context and obj.filter_by_path:
            raise Invalid(_(
                u'news_listing_config_current_context_and_path_error',
                default=u'You can not filter by path and current context '
                        u'at the same time.')
            )
