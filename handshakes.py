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
        return handshakes_list

    @staticmethod
    def get_handshakes(mutual_friends_list):
        results_list = []
        for user_id, name in mutual_friends_list[0].items():
            if user_id in mutual_friends_list[1].keys():
                results_list.append({'id': user_id, 'name': name})
        return results_list


class HandshakesChain:

    def __init__(self):
        self.db = MongoClient()['parse_gb']

    def run(self, handshakes_list, layer):
        collection = self.db['instagram']
        self.get_handshakes_chain(handshakes_list, collection, layer)
        chain_list = self.create_chain(collection, handshakes_list, layer)
        return chain_list

    @staticmethod
    def get_handshakes_chain(handshakes_list, collection, max_layer):
        for layer in range(max_layer, -1, -1):
            for user in handshakes_list:
                user_0 = collection.find({'layer': layer, 'edge': 0, 'follow_id': user['id']})
                for usr_0 in user_0:
                    result_0 = {
                        'user_id': usr_0['user_id'],
                        'user_name': usr_0['user_name'],
                        'type': 'chain',
                        'layer': layer,
                        'edge': 0
                    }
                    collection.insert_one(result_0)

                user_1 = collection.find({'layer': layer, 'edge': 1, 'follow_id': user['id']})
                for usr_1 in user_1:
                    result_1 = {
                        'user_id': usr_1['user_id'],
                        'user_name': usr_1['user_name'],
                        'type': 'chain',
                        'layer': layer,
                        'edge': 1
                    }
                    collection.insert_one(result_1)

    @staticmethod
    def create_chain(collection, handshakes_list, layer):
        chain_list = []
        for el in range(layer + 1):
            temp_list = []
            users = collection.find({'type': 'chain', 'layer': el, 'edge': 0})
            for user in users:
                temp_list.append({'id': user['user_id'], 'name': user['user_name']})
            chain_list.append(temp_list)
        chain_list.append(handshakes_list)
        for el in range(layer, -1, -1):
            temp_list = []
            users = collection.find({'type': 'chain', 'layer': el, 'edge': 1})
            for user in users:
                temp_list.append({'id': user['user_id'], 'name': user['user_name']})
            chain_list.append(temp_list)
        return chain_list


if __name__ == '__main__':
    handshakes = Handshakes()
    handshakes.run([['mr.proghammer'], ['codeforgeyt']], 0)

    handshakes_chain = HandshakesChain()
    chain_list = handshakes_chain.run([{'id': '42371344560', 'name': 'authentic_programmer'}], 0)

    for i, block in enumerate(chain_list):
        print(f'{i + 1}. {block}')
