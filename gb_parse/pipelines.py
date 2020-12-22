# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from typing import Any

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


class MutualFriendsPipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        mutual_friends_list = []
        # adapter = ItemAdapter(item)
        collection = self.db[spider.name]
        users_list = spider.users_list
        # edge = item['edge']
        if item['type'] == 'follow':
            users = collection.find({'user_id': item['user_id'], 'type': 'followed'})
            for user in users:
                if user['followed_id'] == item['follow_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['follow_id'],
                        'mutual_name': item['follow_name'],
                        'type': 'mutual',
                        'edge': user['edge']
                    })
        elif item['type'] == 'followed':
            users = collection.find({'user_id': item['user_id'], 'type': 'follow'})
            for user in users:
                if user['follow_id'] == item['followed_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['followed_id'],
                        'mutual_name': item['followed_name'],
                        'type': 'mutual',
                        'edge': user['edge']
                    })

        mutual_user = []
        for user_0 in collection.find({'type': 'mutual', 'edge': 0}):
            for user_1 in collection.find({'type': 'mutual', 'edge': 1}):
                if user_1['mutual_id'] == user_0['mutual_id']:
                    mutual_user.append({'user_id': user_1['mutual_id'], 'user_name': user_1['mutual_name']})
        if mutual_user:
            print(1)
        return item


class HandshakesPipeline:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        collection = self.db[spider.name]


