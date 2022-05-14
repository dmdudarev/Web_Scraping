import json

import scrapy
from scrapy.http import HtmlResponse
import re
import json
from copy import deepcopy
from urllib.parse import urlencode

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    my_file = open("login.txt", "r")
    lines = my_file.readlines()
    my_login = lines[0].rstrip()
    my_password = lines[1].rstrip()
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['sakhalinkendo', 'eugenesar']
    follows = ['followers', 'following']

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
        j_body = response.json()
        if j_body.get('authenticated'):
            for parse_user in self.parse_users:
                for flw in self.follows:
                    yield response.follow(
                        f'/{parse_user}',
                        callback=self.user_data_parse,
                        cb_kwargs={'username': parse_user,
                                   'flw': flw}
                    )

    def user_data_parse(self, response: HtmlResponse, username, flw):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'search_surface': 'follow_list_page'}
        url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/{flw}/?count=12&{urlencode(variables)}'
        yield response.follow(url_followers,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'flw': flw,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)})

    def user_followers_parse(self, response: HtmlResponse, username, flw, user_id, variables):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['next_max_id'] = j_data.get('next_max_id')
            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/{flw}/?count=12&{urlencode(variables)}'
            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'flw': flw,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})
        print()

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
