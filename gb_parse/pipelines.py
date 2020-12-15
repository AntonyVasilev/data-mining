# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['data']['profile_pic_url']:
            yield Request(item['data'].get('profile_pic_url'))
        else:
            yield Request(item['data'].get('thumbnail_src'))

    def item_completed(self, results, item, info):
        if item['data']['profile_pic_url']:
            return item['data']['profile_pic_url']
        else:
            return item['data']['thumbnail_src']

