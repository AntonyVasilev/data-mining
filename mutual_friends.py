from typing import List, Dict
from pymongo import MongoClient


class MutualFriends:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def run(self, user_names_list, layer):
        # mutual_friends_list = []
        collection = self.db['instagram']
        for user_names in user_names_list:
            for user_name in user_names:
                user_id = collection.find_one({'user_name': user_name})['user_id']
                follow_ids_list = self.get_follow_list(user_name, collection, layer)
                self.get_mutual_friends(user_name, user_id, collection, follow_ids_list, layer)
                # mutual_friends_list.append(mutual_friends)

    @staticmethod
    def get_follow_list(user_name, collection, layer) -> List:
        follow_ids_list = []
        for item in collection.find({'user_name': user_name, 'type': 'follow', 'layer': layer}):
            follow_ids_list.append(item['follow_id'])
        # print(len(follow_ids_list))
        return follow_ids_list

    @staticmethod
    def get_mutual_friends(user_name, user_id, collection, follow_ids_list, layer):
        mutual_friends_dict = {}
        for item in collection.find({'user_name': user_name, 'type': 'followed', 'layer': layer}):
            user_id = item['user_id']
            if item['followed_id'] in follow_ids_list:
                mutual_friends_dict[item['followed_id']] = item['followed_name']
        mutual_friends = {
            'user_id': user_id,
            'user_name': user_name,
            'mutual': mutual_friends_dict,
            'type': 'mutual',
            'layer': layer,
        }
        print(len(mutual_friends_dict))
        print(mutual_friends)
        collection.insert_one(mutual_friends)


if __name__ == '__main__':
    proghamme = MutualFriends()
    proghamme.run([['mr.proghammer'], ['codeforgeyt']], 0)
