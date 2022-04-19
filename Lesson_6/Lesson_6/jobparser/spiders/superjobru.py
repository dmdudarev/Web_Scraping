import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@target='_blank']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse())

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css("h1::text").get()
        salary = response.xpath("//span[@class='_2eYAG -gENC _1TcZY dAWx1']//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
