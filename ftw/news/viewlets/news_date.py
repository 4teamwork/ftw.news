from DateTime import DateTime
from ftw.news.contents.news import INewsSchema
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NewsDateViewlet(ViewletBase):

    template = ViewPageTemplateFile('news_date.pt')

    def render(self):
        return self.template()

    def update(self):
        super(NewsDateViewlet, self).update()
        self.news_date = self.get_news_date()

    def get_news_date(self):
        news_date = INewsSchema(self.context).news_date

        if not news_date:
            return ''

        show_long_format = DateTime(news_date).hour() or DateTime(news_date).minute()
        return self.context.toLocalizedTime(news_date, long_format=show_long_format)
