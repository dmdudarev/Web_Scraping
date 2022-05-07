import scrapy


class CastoramaItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    photos = scrapy.Field()
    url = scrapy.Field()
    _id = scrapy.Field()
