import scrapy


class CastoramaruSpider(scrapy.Spider):
    name = 'castoramaru'
    allowed_domains = ['castorama.ru']
    start_urls = ['http://castorama.ru/']

    def parse(self, response):
        pass
