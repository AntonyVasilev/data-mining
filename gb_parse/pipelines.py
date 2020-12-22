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

        if item['type'] == 'follow':
            users = collection.find({'user_id': item['user_id'], 'type': 'followed', 'layer': item['layer']})
            for user in users:
                if user['followed_id'] == item['follow_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['follow_id'],
                        'mutual_name': item['follow_name'],
                        'type': 'mutual',
                        'layer': item['layer'],
                        'edge': user['edge']
                    })
                    item['has_mutual'] = True
        elif item['type'] == 'followed':
            users = collection.find({'user_id': item['user_id'], 'type': 'follow', 'layer': item['layer']})
            for user in users:
                if user['follow_id'] == item['followed_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['followed_id'],
                        'mutual_name': item['followed_name'],
                        'type': 'mutual',
                        'layer': item['layer'],
                        'edge': user['edge']
                    })
                    item['has_mutual'] = True

        return item


class HandshakesPipeline:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        handshake_user = []
        if item['has_mutual']:
            # users_0 = collection.find({'type': 'mutual', 'edge': 0, 'layer': item['layer']})
            # for user_0 in users_0:
            #     user_1 = collection.find_one({'mutual_id': user_0['mutual_id'], 'type': 'mutual',
            #                                   'edge': 1, 'layer': item['layer']})
            #     if user_1:
            #         handshake_user.append({'user_id': user_1['mutual_id'], 'user_name': user_1['mutual_name']})
            # users_1 = collection.find({'type': 'mutual', 'edge': 1, 'layer': item['layer']})
            for user_0 in collection.find({'type': 'mutual', 'edge': 0, 'layer': item['layer']}):
                for user_1 in collection.find({'type': 'mutual', 'edge': 1, 'layer': item['layer']}):
                    if user_0['mutual_id'] == user_1['mutual_id']:
                        print(1)
                        handshake_user.append({'user_id': user_1['mutual_id'], 'user_name': user_1['mutual_name']})
        return item

