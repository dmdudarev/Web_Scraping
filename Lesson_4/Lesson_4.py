from lxml import html
import requests
from hashlib import md5
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re

client = MongoClient('127.0.0.1', 27017)
db = client['news']
collection = db.lesson4

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  \
             Chrome/100.0.4896.60 Safari/537.36'
headers = {'User-Agent': user_agent}
url = 'https://lenta.ru'


def hash_id(doc):
    doc_input = str(doc).encode('utf-8')

    return md5(doc_input).hexdigest()


response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
link_top = dom.xpath("//a[@class='card-big _topnews _news']")  # Ссылка на главную новость
links = dom.xpath("//a[@class='card-mini _topnews']")  # Ссылки на остальные новости
links.insert(0, link_top[0])

num_add = 0
num_dupl = 0

for link in links:
    tdb = {}
    if link.xpath("./@href")[0][0] != "/":
        # В ленту могут попасть сторонние новости - https://moslenta.ru/news/city/malysheva-29-04-2022.htm
        new_link = link.xpath("./@href")[0]
        name_news = link.xpath(".//text()")[0]
        a = new_link.find('//') + 2  # Начало домена 2 уровня
        b = new_link.find('/', a)  # Конец домена 1 уровня
        source = new_link[a:b]
        match_date = re.findall('\d{2}.\d{2}.\d{4}', new_link)[0]
        time_tag = link.xpath(".//time/text()")[0]
        date_news = time_tag + ', ' + match_date
    else:
        new_link = url + link.xpath("./@href")[0]
        name_news = link.xpath(".//text()")[0]
        source = 'lenta.ru'
        match_date = re.findall('\d{4}.\d{2}.\d{2}', new_link)[0]
        time_tag = link.xpath(".//time/text()")[0]
        date_news = time_tag + ', ' + match_date[8:] + '-' + match_date[5:7] + '-' + match_date[:4]

    tdb['name'] = name_news
    tdb['date_time'] = date_news
    tdb['source'] = source
    tdb['link'] = new_link
    _id = hash_id(tdb)
    tdb['_id'] = _id

    try:
        collection.insert_one(tdb)
        num_add += 1
    except DuplicateKeyError:
        num_dupl += 1

print(f"Добавлено: {num_add}; пропущено дубликатов: {num_dupl}")
