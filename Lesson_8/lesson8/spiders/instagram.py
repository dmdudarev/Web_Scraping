import scrapy
from scrapy.http import HtmlResponse
import re

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    my_file = open("login.txt", "r")
    lines = my_file.readlines()
    my_login = lines[0].rstrip()
    my_password = lines[1].rstrip()
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.my_login, 'enc_password': self.my_password},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        print()

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')