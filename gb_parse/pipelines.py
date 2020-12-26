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
# from scrapy.project import crawler
import functools
import json


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item


class HandshakesPipeline:

    def close_spider(self, spider):
        print(f'The shortest path between A and B is:')

    def process_item(self, item, spider):
        has_path = False
        paths_list = []
        is_two_way_path = False
        users_list = spider.users_list

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

        try:
            has_path = nx.has_path(spider.G, users_list[0], users_list[1])
        except nx.exception.NodeNotFound:
            pass

        if not has_path:
            pass
        else:
            shortest_path = nx.shortest_path(spider.G, users_list[0], users_list[1])
            shortest_path.reverse()
            for j in range(len(shortest_path) - 1):
                temp_path = nx.shortest_path(spider.G, shortest_path[j], shortest_path[j + 1])
                if len(temp_path) == 2:
                    paths_list.append(True)
                else:
                    paths_list.append(False)
            if False not in paths_list:
                is_two_way_path = True

            shortest_path.reverse()
            if is_two_way_path:
                # print('\n\n\n\n\n')
                # print(f'The shortest path between {users_list[0]} and {users_list[1]} is:')
                # for i, user_name in enumerate(shortest_path):
                #     print(f'{i + 1}. User name: {user_name}')
                # print('\n\n\n\n\n')
                spider.crawler.engine.close_spider(self, reason='Handshake\'s chain is found')

        return item


    # def close_spider(self, spider):
    #     users_list = spider.users_list
    #     print(f'The shortest path between {users_list[0]} and {users_list[1]} is:')
    #     for i, user_name in enumerate(self.shortest_path):
    #         print(f'{i + 1}. User name: {user_name}')
