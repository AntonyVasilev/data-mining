from pymongo import MongoClient


class Handshakes:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def run(self, user_names_list, layer):
        mutual_friends_list = []
        collection = self.db['instagram']
        for users in user_names_list:
            temp_dict = {}
            for user in users:
                mutual_list = collection.find_one({'user_name': user, 'type': 'mutual', 'layer': layer})['mutual']
                for key, value in mutual_list.items():
                    temp_dict[key] = value
            mutual_friends_list.append(temp_dict)
        handshakes_list = self.get_handshakes(mutual_friends_list)
        # print(mutual_friends_list)
        handshakes_chain = self.get_handshakes_chain(user_names_list[0], user_names_list[1],
                                                     handshakes_list, collection, layer)
        return True if handshakes_list else False

    @staticmethod
    def get_handshakes(mutual_friends_list):
        results_list = []
        for user_id, name in mutual_friends_list[0].items():
            if user_id in mutual_friends_list[1].keys():
                results_list.append({'id': user_id, 'name': name})
        return results_list

    def get_handshakes_chain(self, users_list_0, users_list_1, handshakes_list, collection, layer):
        for user in handshakes_list:
            h_shaked_users = collection.find({'follow_id': user['id'], 'layer': layer})
            for h_sh_user in h_shaked_users:
                print(1)

if __name__ == '__main__':
    handshakes = Handshakes()
    handshakes.run([['mr.proghammer'], ['codeforgeyt']], 0)
