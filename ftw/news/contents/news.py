import datetime
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.news import _
from ftw.news.interfaces import INews
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.interface import implements


def default_news_date():
    return datetime.datetime.now()


class INewsSchema(form.Schema):
    """
    This schema represents a news item.
    """
    form.widget('news_date', DatePickerFieldWidget)
    news_date = schema.Datetime(
        title=_(u'news_date_label', default=u'Date'),
        description=_(u'news_date_description',
                      default=u'News will be sorted by this date'),
        required=True,
        defaultFactory=default_news_date,
    )


class News(Container):
    implements(INews)
