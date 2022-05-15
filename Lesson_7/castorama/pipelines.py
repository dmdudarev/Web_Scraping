import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from hashlib import md5
from scrapy.pipelines.images import ImagesPipeline


class CastoramaPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.castorama_ls7

    def process_item(self, item, spider):
        _id = md5(str(item).encode('utf-8')).hexdigest()
        item['_id'] = _id

        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            None

        return item


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
