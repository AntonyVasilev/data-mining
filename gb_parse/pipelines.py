# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Request, pipelines
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
        collection = self.db[spider.name]

        if item['type'] == 'follow':
            users = collection.find({'user_id': item['user_id'], 'type': 'followed'})
            for user in users:
                if user['followed_id'] == item['follow_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['follow_id'],
                        'mutual_name': item['follow_name'],
                        'type': 'mutual'
                    })
                    spider.mutual_names.add(item['follow_name'])
        elif item['type'] == 'followed':
            users = collection.find({'user_id': item['user_id'], 'type': 'follow'})
            for user in users:
                if user['follow_id'] == item['followed_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['followed_id'],
                        'mutual_name': item['followed_name'],
                        'type': 'mutual'
                    })
                    spider.mutual_names.add(item['followed_name'])

        return item


class HandshakesPipeline:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        collection = self.db[spider.name]

        handshake_users = []
        mutual_0_list = []
        mutual_1_list = []

        users_0 = [spider.users_list[0]]
        users_1 = [spider.users_list[1]]

        while not handshake_users:
            for user_0 in users_0:
                users_0_list = collection.find({'user_name': user_0, 'type': 'mutual'})
                for mutual_0 in users_0_list:
                    mutual_0_list.append(mutual_0['mutual_name'])
            for user_1 in users_1:
                users_1_list = collection.find({'user_name': user_1, 'type': 'mutual'})
                for mutual_1 in users_1_list:
                    mutual_1_list.append(mutual_1['mutual_name'])

            if not mutual_0_list or mutual_1_list:
                break

            for user in mutual_0_list:
                if user in mutual_1_list:
                    user_id = collection.find_one({'mutual_name': user})
                    collection.insert_one({
                        'user_id': user_id,
                        'user_name': user
                    })
                    spider.close_down = True

        return item
