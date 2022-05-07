from itemadapter import ItemAdapter
from pymongo import MongoClient
from hashlib import md5


class CastoramaPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.castorama_ls7

    def process_item(self, item, spider):
        _id = hash_id(item)
        item['_id'] = _id
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def hash_id(doc):
        doc_input = str(doc).encode('utf-8')

        return md5(doc_input).hexdigest()
