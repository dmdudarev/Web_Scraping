import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def convert_price(value):
    try:
        return float(value)
    except:
        return value

class CastoramaItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
