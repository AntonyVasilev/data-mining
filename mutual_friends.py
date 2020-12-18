from typing import List, Dict
from pymongo import MongoClient


class MutualFriends:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def run(self, user_id):
        follow_ids_list = self.get_follow_list(user_id)
        mutual_friends = self.get_mutual_friends(user_id, follow_ids_list)
        print(mutual_friends)

    def get_follow_list(self, user_id) -> List:
        collection = self.db['instagram']
        follow_ids_list = []
        for item in collection.find({'user_id': user_id, 'type': 'follow'}):
            follow_ids_list.append(item['follow_id'])
        print(len(follow_ids_list))
        return follow_ids_list

    def get_mutual_friends(self, user_id, follow_ids_list) -> Dict:
        mutual_friends_dict = {}
        collection = self.db['instagram']
        for item in collection.find({'user_id': user_id, 'type': 'followed'}):
            if item['followed_id'] in follow_ids_list:
                mutual_friends_dict[item['followed_id']] = item['followed_name']
        print(len(mutual_friends_dict))
        return mutual_friends_dict


if __name__ == '__main__':
    proghamme = MutualFriends()
    proghamme.run('36636112793')

    codeforgeyt = MutualFriends()
    codeforgeyt.run('8650028000')
