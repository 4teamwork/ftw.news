from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.news.contents.news import INewsSchema
from plone.app.layout.viewlets import ViewletBase
import datetime


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

        news_date = datetime.datetime.combine(self.context.news_date,
                                              datetime.time.min)
        return self.context.toLocalizedTime(news_date)
