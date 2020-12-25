from pymongo import MongoClient
import networkx as nx
import matplotlib.pyplot as plt


class GraphMaker:

    def __init__(self, users_list):
        self.db = MongoClient()['parse_gb']
        self.users_list = users_list

    def run(self):
        collection = self.db['instagram']
        G = nx.DiGraph()
        follow_users = collection.find({'type': 'follow'})
        followed_users = collection.find({'type': 'followed'})

        node_a = collection.find_one({'user_name': self.users_list[0]})['user_id']
        node_b = collection.find_one({'user_name': self.users_list[1]})['user_id']

        for f_user in follow_users:
            G.add_nodes_from([f_user['user_id'], f_user['follow_id']])
            G.add_edge(f_user['user_id'], f_user['follow_id'])

        for fd_user in followed_users:
            G.add_nodes_from([fd_user['user_id'], fd_user['followed_id']])
            G.add_edge(fd_user['followed_id'], fd_user['user_id'])

        has_path_ab = nx.has_path(G, node_a, node_b)
        has_path_ba = nx.has_path(G, node_b, node_a)

        if has_path_ab and has_path_ba:
            shortest_path = nx.shortest_path(G, node_a, node_b)

            for i, user_id in enumerate(shortest_path):
                user_name = collection.find_one({'user_id': user_id})['user_name']
                print(f'{i + 1}. id: {user_id}, name: {user_name}')
        input()



if __name__ == '__main__':
    gr = GraphMaker(['mr.proghammer', 'codeforgeyt'])
    gr.run()