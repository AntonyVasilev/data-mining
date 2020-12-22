
import json
import scrapy
from ..items import InstagramFollow, InstagramFollowed


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    db_type = 'MONGO'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    api_url = '/graphql/query/'
    query_hash = {
        'tag_posts': '9b498c08113f1e09617a1703c22b2f32',
        'posts': '56a7068fea504063273cc2120ffd54f3',
        'follow': 'd04b0a864b4b54837c0d870b0e77e076',
        'followers': 'c76146de99bb02f6415203be841dd25a'
    }

    follow_ids_list = []
    mutual_friends_dict = {}

    def __init__(self, login, password, users_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.users_list = users_list
        super(InstagramSpider, self).__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        edge = 0
        if self.follow_ids_list:
            self.follow_ids_list.clear()
        if self.mutual_friends_dict:
            self.mutual_friends_dict.clear()
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for user in self.users_list:
                    yield response.follow(f'/{user}', callback=self.user_parse, cb_kwargs={'edge': edge})
                    edge += 1

    def user_parse(self, response, edge):
        data = self.js_data_extract(response)
        user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']

        yield from self.get_follow_api_request(response, user_data, edge)
        yield from self.get_followed_api_request(response, user_data, edge)

    def get_follow_api_request(self, response, user_data, edge, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100
            }

        follow_url = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
        yield response.follow(follow_url, callback=self.get_follow_api,
                              cb_kwargs={'user_data': user_data, 'edge': edge})

    def get_follow_api(self, response, user_data, edge):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield from self.get_follow_item(response, user_data, data['data']['user']['edge_follow']['edges'], edge)

            if data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_follow']['page_info']['end_cursor']
                }
                yield from self.get_follow_api_request(response, user_data, edge, variables)

    def get_follow_item(self, response, user_data, follow_users_data, edge):
        for follow_user in follow_users_data:
            self.follow_ids_list.append(follow_user['node']['id'])
            yield InstagramFollow(
                user_id=user_data['id'],
                user_name=user_data['username'],
                follow_id=follow_user['node']['id'],
                follow_name=follow_user['node']['username'],
                type='follow',
                # layer=self.layer,
                edge=edge
            )
            # yield response.follow(f'/{follow_user["node"]["username"]}', callback=self.user_parse, cb_kwargs={'edge': edge})


    def get_followed_api_request(self, response, user_data, edge, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100
            }

        followed_url = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(followed_url, callback=self.get_followed_api,
                              cb_kwargs={'user_data': user_data, 'edge': edge})

    def get_followed_api(self, response, user_data, edge):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield from self.get_followed_item(user_data, data['data']['user']['edge_followed_by']['edges'], edge)

            if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor']
                }
                yield from self.get_followed_api_request(response, user_data, edge, variables)

    def get_followed_item(self, user_data, follow_users_data, edge):
        for followed_user in follow_users_data:
            if followed_user['node']['id'] in self.follow_ids_list:
                self.mutual_friends_dict[followed_user['node']['id']] = followed_user['node']['username']
            yield InstagramFollowed(
                user_id=user_data['id'],
                user_name=user_data['username'],
                followed_id=followed_user['node']['id'],
                followed_name=followed_user['node']['username'],
                type='followed',
                # layer=self.layer,
                edge=edge
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])