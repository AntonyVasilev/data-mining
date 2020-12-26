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
import functools


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
        has_path_ab = False
        has_path_ba = False
        users_list = spider.users_list
        collection = self.db['instagram']

        # try:
        #     node_a = collection.find_one({'user_name': users_list[0]})['user_id']
        #     node_b = collection.find_one({'user_name': users_list[1]})['user_id']
        # except TypeError:
        #     pass

        if item['type'] == 'follow':
            if item['user_name'] not in spider.G.nodes:
                spider.G.add_node(item['user_name'])
            if item['follow_name'] not in spider.G.nodes:
                spider.G.add_node(item['follow_name'])
            spider.G.add_edge(item['user_name'], item['follow_name'])
        elif item['type'] == 'followed':
            if item['user_name'] not in spider.G.nodes:
                spider.G.add_node(item['user_name'])
            if item['followed_name'] not in spider.G.nodes:
                spider.G.add_node(item['followed_name'])
            spider.G.add_edge(item['followed_name'], item['user_name'])

        # print(spider.G.nodes)
        try:
            has_path_ab = nx.has_path(spider.G, users_list[0], users_list[1])
            has_path_ba = nx.has_path(spider.G, users_list[1], users_list[0])
        except nx.exception.NodeNotFound:
            pass

        # if has_path_ab:
        #     pass
        # elif has_path_ba:
        #     pass

        if not has_path_ab or not has_path_ba:
            pass
        else:
            shortest_path_ab = nx.shortest_path(spider.G, users_list[0], users_list[1])
            shortest_path_ba = nx.shortest_path(spider.G, users_list[1], users_list[0])
            shortest_path_ba.reverse()
            # print(1)
            # if shortest_path_ab == shortest_path_ba.reverse():
            if functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q, shortest_path_ab, shortest_path_ba), True):
                for i, user_name in enumerate(shortest_path_ab):
                    print(f'{i + 1}. User name: {user_name}')

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
