import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from hashlib import md5
from scrapy.pipelines.images import ImagesPipeline


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


class CastoramaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]

        return item
