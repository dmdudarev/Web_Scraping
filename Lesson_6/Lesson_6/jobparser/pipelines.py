# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from hashlib import md5
from unicodedata import normalize


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy_ls6

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_hh(item['salary'])
        else:
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_sj(item['salary'])
        del item['salary']
        _id = hash_id(item)
        item['_id'] = _id
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        # Обработка зарплаты для сайта hh.ru
        if len(salary) != 1:
            currency = salary[-1]
            if salary[0] == 'до':
                max_salary = float(normalize('NFKD', salary[1]))
                min_salary = None
            elif salary[0] == 'от':
                min_salary = float(normalize('NFKD', salary[1]))
                if salary[2] == 'до':
                    max_salary = float(normalize('NFKD', salary[3]))
                else:
                    max_salary = None
        else:
            min_salary, max_salary, currency = [None] * 3

        return min_salary, max_salary, currency

    def process_salary_sj(self, salary):
        # Обработка зарплаты для сайта superjob.ru
        if len(salary) == 1:
            min_salary, max_salary, currency = [None] * 3
        elif len(salary) == 4:
            min_salary = float(normalize('NFKD', salary[0]))
            max_salary = float(normalize('NFKD', salary[1]))
            currency = salary[-1]
        else:
            if salary[0] == 'до':
                a = str()
                l = 0
                for b in salary[-1]:
                    if b.isdigit():
                        a += b
                max_salary = float(a)
                min_salary = None
                currency = salary[-1][l:]

            elif salary[0] == 'от':
                a = str()
                l = 0
                for b in salary[-1]:
                    if b.isdigit():
                        a += b
                        l += 1
                max_salary = None
                min_salary = float(a)
                currency = salary[-1][l:]
            else:
                min_salary = float(normalize('NFKD', salary[0]))
                max_salary = min_salary
                currency = salary[-1]

        return min_salary, max_salary, currency


def hash_id(doc):
    doc_input = str(doc).encode('utf-8')

    return md5(doc_input).hexdigest()
