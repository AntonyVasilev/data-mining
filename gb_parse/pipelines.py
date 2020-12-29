# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from typing import Any

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
        self.shortest_path = []

    def process_item(self, item, spider):
        has_path_ab = False
        has_path_ba = False
        collection = self.db[spider.name]
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
            has_path_ab = nx.has_path(spider.G, users_list[0], users_list[1])
            has_path_ba = nx.has_path(spider.G, users_list[1], users_list[0])
        except nx.exception.NodeNotFound:
            pass
        except nx.exception.NetworkXNoPath:
            pass

        if not has_path_ab or not has_path_ba:
            pass
        else:
            shortest_path = nx.shortest_path(spider.G, users_list[0], users_list[1])
            return_paths = nx.all_shortest_paths(spider.G, users_list[1], users_list[0])
            for return_path in return_paths:
                return_path.reverse()
                if shortest_path == return_path:
                    is_two_way_path = True

            if is_two_way_path:
                print('\n\n\n')
                print(shortest_path)
                print('\n\n\n')

                collection.insert_one({
                    'start_user_name': users_list[0],
                    'target_user_name': users_list[1],
                    'handshakes_chain': shortest_path,
                    'type': 'chain'}
                )

                spider.crawler.engine.close_spider(self, reason='Handshake\'s chain is found')

        return item
