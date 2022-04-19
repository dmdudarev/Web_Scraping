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
        item['min_salary'], item['max_salary'], item['currency'] = self.process_salary(item['salary'])
        del item['salary']
        _id = hash_id(item)
        item['_id'] = _id
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_salary(self, salary):

        if len(salary) != 1:
            currency = salary[-1]
            if salary[0] == 'до':  # 'от':
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

    def hash_id(doc):
        doc_input = str(doc).encode('utf-8')

        return md5(doc_input).hexdigest()
