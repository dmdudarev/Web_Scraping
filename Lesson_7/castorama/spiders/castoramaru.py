import scrapy
from scrapy.http import HtmlResponse
from castorama.items import CastoramaItem
from scrapy.loader import ItemLoader


class CastoramaruSpider(scrapy.Spider):
    name = 'castoramaru'
    allowed_domains = ['castorama.ru']
    start_urls = ['https://www.castorama.ru/gardening-and-outdoor/pressure-washers']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[contains(@class, 'product-card__name')]/@href")
        for link in links:
            yield response.follow(link, callback=self.castorama_parse)

    def castorama_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=CastoramaItem(), response=response)
        loader.add_xpath('name', "//h1[@class='product-essential__name hide-max-small']/text()")
        loader.add_xpath('price', "//span[@itemprop='price']/@content")
        loader.add_xpath('photos', "//li[contains(@class, 'top-slide')]//span/@content")
        loader.add_value('url', response.url)
        yield loader.load_item()
