import scrapy
from scrapy.http import HtmlResponse
from castorama.items import CastoramaItem


class CastoramaruSpider(scrapy.Spider):
    name = 'castoramaru'
    allowed_domains = ['castorama.ru']
    start_urls = ['https://www.castorama.ru/gardening-and-outdoor/pressure-washers']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='product-card__name ga-product-card-name']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.cactorama_parse())

    def cactorama_parse(self, response: HtmlResponse):
        name = response.xpath("//h1[@class='product-essential__name hide-max-small']/text()").get()
        photos = response.xpath("//img[contains(@class, 'top-slide__img swiper-lazy')]/@src").getall()
        price = response.xpath("//div[@class ='current-price']//text()").get()
        url = response.url
        yield CastoramaItem(name=name, price=price, photos=photos, url=url)
