import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from turkishbankuk.items import Article


class TurkukSpider(scrapy.Spider):
    name = 'turkuk'
    start_urls = ['https://www.turkishbank.co.uk/category/banking-news/']

    def parse(self, response):
        month_names = response.xpath('//h3[@class="fusion-timeline-date"]/text()').getall()
        month_div = response.xpath('//div[@class="fusion-collapse-month"]')
        for i, month in enumerate(month_div):
            articles = month.xpath('.//article')
            for article in articles:
                link = article.xpath('.//h2/a/@href').get()
                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=month_names[i]))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = datetime.strptime(date, '%B %Y')
        date = date.strftime('%Y/%m')
        content = response.xpath('//div[@class="post-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
