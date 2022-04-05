from bs4 import BeautifulSoup as bs
import requests as req
import pandas as pd
from random import randint as rndi
from time import sleep
import pprint as pprint


def get_hh_compensations(item):
    # сбор данных о зарплате
    try:
        vac_compensation = item.find('div', {'class': 'vacancy-serp-item__compensation'}).getText()
    except:
        vac_compensation = None
    if vac_compensation != None:
        vac_compensation = vac_compensation.split(' ')
        comp_curr = vac_compensation[-1]
        if vac_compensation[0] == 'от':
            min_compensation = ''.join(vac_compensation[1:-1])
            max_compensation = None
        elif vac_compensation[0] == 'до':
            max_compensation = ''.join(vac_compensation[1:-1])
            min_compensation = None
        else:
            min_compensation = vac_compensation[0].split('-')[0]
            max_compensation = vac_compensation[0].split('-')[1]
    else:
        min_compensation, max_compensation, comp_curr = [None] * 3
    return min_compensation, max_compensation, comp_curr


def get_hh_data(vacancies):
    # сбор данных: название, ссылка и т.д.
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
            location = item.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).getText()
        except:
            location = None
        min_compensation, max_compensation, comp_curr = get_hh_compensations(item)
        df.loc[len(df) + 1] = [vac_name, employer, location, min_compensation, max_compensation,
                               comp_curr, vac_link, site_name]


df = pd.DataFrame(columns=['vac_name', 'employer', 'location', 'min_compensation', 'max_compensation',
                           'currency', 'link', 'site_name'])

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/78.0.3904.97 Safari/537.36'
headers = {'User-Agent': user_agent}
hh = 'https://hh.ru'

search_text = input('Что ищем? ')
if search_text == '':
    search_text = 'Data scientist'

response = req.get(hh + f'/search/vacancy?text={search_text}', headers=headers)
if response.ok:
    hh_parsed_html = bs(response.text, 'html.parser')
    try:
        hh_vacancies_total = hh_parsed_html.find('div', {'class': 'breadcrumbs'}).next_sibling.getText()
    except:
        hh_vacancies_total = 0
    try:
        hh_pages_total = int(hh_parsed_html.find_all('a', {'data-qa': 'pager-page'})[-1].getText())
    except:
        hh_pages_total = 0
else:
    print('error', response.status_code)

print(f'на {hh} найдено {hh_vacancies_total}. всего страниц {hh_pages_total}')
input_pages = input('Сколько страниц будем парсить? ')
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
        hh_vacancies_block = hh_parsed_html.find('div', {'class': 'vacancy-serp'})
        hh_vacancies = hh_vacancies_block.findChildren('div', {'class': 'vacancy-serp-item'}, recursive=False)
        get_hh_data(hh_vacancies)
    else:
        hh_err_log[page + 1] = response.status_code
        continue
    sleep(rndi(1, 5))
if hh_err_log != {}:
    print('не все прошло гладко - "номер страницы":"статус запроса"', hh_err_log)

pprint(df)
