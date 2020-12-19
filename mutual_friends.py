from typing import List, Dict
from pymongo import MongoClient


class MutualFriends:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def run(self, user_names):
        mutual_friends_list = []
        for user_name in user_names:
            follow_ids_list = self.get_follow_list(user_name)
            mutual_friends = self.get_mutual_friends(user_name, follow_ids_list)
            mutual_friends_list.append(mutual_friends)

        handshakes = self.get_handshakes(mutual_friends_list)
        print(handshakes)
        # return handshakes, mutual_friends_list

    def get_follow_list(self, user_name) -> List:
        collection = self.db['instagram']
        follow_ids_list = []
        for item in collection.find({'user_name': user_name, 'type': 'follow'}):
            follow_ids_list.append(item['follow_id'])
        # print(len(follow_ids_list))
        return follow_ids_list

    def get_mutual_friends(self, user_name, follow_ids_list) -> Dict:
        mutual_friends_dict = {}
        collection = self.db['instagram']
        for item in collection.find({'user_name': user_name, 'type': 'followed'}):
            if item['followed_id'] in follow_ids_list:
                mutual_friends_dict[item['followed_id']] = item['followed_name']
        # print(len(mutual_friends_dict))
        return mutual_friends_dict

    @staticmethod
    def get_handshakes(mutual_friends_list):
        results_list = []
        list_len = len(mutual_friends_list)
        for i in range(list_len - 1):
            temp_list = []
            for user_id, user_name in mutual_friends_list[i].items():
                if user_id in mutual_friends_list[i + 1].keys():
                    temp_list.append({user_id: user_name})
            results_list.append(temp_list)
        return results_list


if __name__ == '__main__':
    proghamme = MutualFriends()
    proghamme.run(['mr.proghammer', 'codeforgeyt'])
