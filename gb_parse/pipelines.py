# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from scrapy import Request
from pymongo import MongoClient


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item


# class MutualFriends:
#
#     def __init__(self):
#         self.db = MongoClient()['parse_gb']
#
#     def


# class GbImagePipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         if item['type'] == 'tag':
#             img_url = item['data'].get('profile_pic_url')
#         elif item['type'] == 'post':
#             img_url = item['data'].get('thumbnail_src')
#         elif item['type'] == 'user':
#             img_url = item['data'].get('profile_pic_url_hd')
#         elif item['type'] == 'follower':
#             img_url = item['profile_pic_url']
#         else:
#             pass
#         yield Request(img_url)

    # def item_completed(self, results, item, info):
    #     if item['type'] == 'tag':
    #         item['data']['profile_pic_url'] = [itm[1] for itm in results]
    #     elif item['type'] == 'post':
    #         item['data']['thumbnail_src'] = [itm[1] for itm in results]
    #     elif item['type'] == 'user':
    #         item['data']['profile_pic_url_hd'] = [itm[1] for itm in results]
    #     elif item['type'] == 'follower':
    #         item['profile_pic_url'] = [itm[1] for itm in results]
    #     else:
    #         pass
    #     return item
