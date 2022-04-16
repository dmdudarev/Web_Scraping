import scrapy


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://engels.hh.ru/search/vacancy?text=Python&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true',
                  'https://engels.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=Python&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true']

    def parse(self, response):
        print(response.url)
