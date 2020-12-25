# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Request, pipelines
from pymongo import MongoClient
import networkx as nx


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item


class HandshakesPipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        users_list = spider.users_list
        collection = self.db['instagram']
        G = nx.DiGraph()

        node_a = collection.find_one({'user_name': users_list[0]})['user_id']
        node_b = collection.find_one({'user_name': users_list[1]})['user_id']

        if item['type'] == 'follow':
            G.add_nodes_from([item['user_id'], item['follow_id']])
            G.add_edge(item['user_id'], item['follow_id'])

        if item['type'] == 'follow':
            G.add_nodes_from([item['user_id'], item['followed_id']])
            G.add_edge(item['followed_id'], item['user_id'])

        has_path_ab = nx.has_path(G, node_a, node_b)
        has_path_ba = nx.has_path(G, node_b, node_a)

        if has_path_ab and has_path_ba:
            shortest_path = nx.shortest_path(G, node_a, node_b)

            for i, user_id in enumerate(shortest_path):
                user_name = collection.find_one({'user_id': user_id})['user_name']
                print(f'{i + 1}. id: {user_id}, name: {user_name}')

        return item


class MutualFriendsPipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        collection = self.db[spider.name]

        if item['type'] == 'follow':
            users = collection.find({'user_id': item['user_id'], 'type': 'followed'})
            # spider.mutual_names.add(item['follow_name'])
            for user in users:
                if user['followed_id'] == item['follow_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['follow_id'],
                        'mutual_name': item['follow_name'],
                        'type': 'mutual'
                    })
        elif item['type'] == 'followed':
            users = collection.find({'user_id': item['user_id'], 'type': 'follow'})
            # spider.mutual_names.add(item['followed_name'])
            for user in users:
                if user['follow_id'] == item['followed_id']:
                    collection.insert_one({
                        'user_id': user['user_id'],
                        'user_name': user['user_name'],
                        'mutual_id': item['followed_id'],
                        'mutual_name': item['followed_name'],
                        'type': 'mutual'
                    })
        return item


# class HandshakesPipeline:
#
#     def __init__(self):
#         self.db = MongoClient()['parse_gb']
#
#     def process_item(self, item, spider):
#         collection = self.db[spider.name]
#
#         handshake_users = []
#         mutual_0_list = []
#         mutual_1_list = []
#
#         users_0 = [spider.users_list[0]]
#         users_1 = [spider.users_list[1]]
#
#         while not handshake_users:
#             for user_0 in users_0:
#                 users_0_list = collection.find({'user_name': user_0, 'type': 'mutual'})
#                 for mutual_0 in users_0_list:
#                     mutual_0_list.append(mutual_0['mutual_name'])
#             for user_1 in users_1:
#                 users_1_list = collection.find({'user_name': user_1, 'type': 'mutual'})
#                 for mutual_1 in users_1_list:
#                     mutual_1_list.append(mutual_1['mutual_name'])
#
#             if not mutual_0_list or mutual_1_list:
#                 break
#
#             for user in mutual_0_list:
#                 if user in mutual_1_list:
#                     user_id = collection.find_one({'mutual_name': user})
#                     collection.insert_one({
#                         'user_id': user_id,
#                         'user_name': user
#                     })
#                     spider.close_down = True
#
#         return item
