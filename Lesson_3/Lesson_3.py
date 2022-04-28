from bs4 import BeautifulSoup as bs
import requests as req
from pprint import pprint
from hashlib import md5
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from random import randint as rndi
from time import sleep

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
collection = db.lesson3

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  \
             Chrome/100.0.4896.60 Safari/537.36'
headers = {'User-Agent': user_agent}
hh = 'https://hh.ru'

search_text = input('Введите вакансию для поиска: ')
if search_text == '':
    search_text = 'Data scientist'


def hash_id(doc):
    doc_input = str(doc).encode('utf-8')

    return md5(doc_input).hexdigest()

def get_hh_compensations(item):
    # сбор данных о зарплате
    try:
        vac_compensation = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
    except:
        vac_compensation = None
    if vac_compensation != None:
        vac_compensation = vac_compensation.split(' ')
        comp_curr = vac_compensation[-1]
        if vac_compensation[0] == 'от':
            min_compensation = float(''.join(vac_compensation[1:-1]).replace('\u202f', ''))
            max_compensation = None
        elif vac_compensation[0] == 'до':
            max_compensation = float(''.join(vac_compensation[1:-1]).replace('\u202f', ''))
            min_compensation = None
        else:
            min_compensation = float(vac_compensation[0].replace('\u202f', ''))
            max_compensation = float(vac_compensation[2].replace('\u202f', ''))
    else:
        min_compensation, max_compensation, comp_curr = [None] * 3
    return min_compensation, max_compensation, comp_curr

def get_hh_data(vacancies):
    # сбор данных: название, ссылка и т.д.
    num_add = 0
    num_dupl = 0
    for item in vacancies:
        site_name = hh
        try:
            vac_name = item.find('a').getText()
        except:
            vac_name = None
        try:
            vac_link = item.find('a')['href']
        except:
            vac_link = None
        try:
            employer = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
        except:
            employer = None
        try:
            location = item.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText()
        except:
            location = None
        min_compensation, max_compensation, comp_curr = get_hh_compensations(item)
        print(vac_name, min_compensation, max_compensation, comp_curr)
        # tdb = {}
        # tdb['vac_name'] = vac_name
        # tdb['employer'] = employer
        # tdb['location'] = location
        # tdb['vac_link'] = vac_link
        # tdb['min_compensation'] = min_compensation
        # tdb['max_compensation'] = max_compensation
        # tdb['comp_curr'] = comp_curr
        # _id = hash_id(tdb)
        # tdb['_id'] = _id
        #
        # try:
        #     collection.insert_one(tdb)
        #     num_add += 1
        # except DuplicateKeyError:
        #     num_dupl += 1

response = req.get(hh + f'/search/vacancy?text={search_text}', headers=headers)
if response.ok:
    hh_parsed_html = bs(response.text, 'html.parser')
    try:
        hh_vacancies_total = hh_parsed_html.find('h1', {'class': 'bloko-header-section-3'}).getText()
    except:
        hh_vacancies_total = 0
    try:
        hh_pages_total = int(hh_parsed_html.find_all('a', {'data-qa': 'pager-page'})[-1].getText())
    except:
        hh_pages_total = 0
else:
    print('error', response.status_code)

print(f'на {hh} найдено {hh_vacancies_total}. всего страниц {hh_pages_total}')
input_pages = input('Сколько страниц обработать? ')
try:
    hh_pages = int(input_pages)
except:
    hh_pages = 0
if hh_pages > hh_pages_total:
    hh_pages = hh_pages_total
elif hh_pages < 1:
    hh_pages = 0

hh_err_log = {}
for page in range(hh_pages):
    response = req.get(hh + f'/search/vacancy?text={search_text}&page={page}', headers=headers)
    if response.status_code == 200:
        hh_parsed_html = bs(response.text, 'html.parser')
        hh_vacancies_block = hh_parsed_html.find('div', {'data-qa': 'vacancy-serp__results'})
        hh_vacancies = hh_vacancies_block.findChildren('div', {'class': 'vacancy-serp-item'}, recursive=False)
        get_hh_data(hh_vacancies)
    else:
        hh_err_log[page + 1] = response.status_code
        continue
    sleep(rndi(1, 5))
if hh_err_log != {}:
    print('при сборе данных произошли ошибки - "номер страницы":"статус запроса"', hh_err_log)
