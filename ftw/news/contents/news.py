from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.news import _
from ftw.news.interfaces import INews
from plone.dexterity.content import Container
from plone.directives import form
from plone.supermodel import model
from zope import schema
from zope.interface import implements


class INewsSchema(model.Schema):
    """
    This schema represents a news item..
    """
    form.widget(news_date=DatePickerFieldWidget)
    news_date = schema.Date(
        title=_(u'news_date_label', default=u'Date'),
        description=_(u'news_date_description',
                      default=u'News will be sorted by this date'),
        required=True,
    )


class News(Container):
    implements(INews)
