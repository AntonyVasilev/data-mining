import datetime
import json
import scrapy
from ..items import InstagramTag, InstagramPost, InstagramUser


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    db_type = 'MONGO'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    api_url = '/graphql/query/'
    query_hash = {
        'tag_posts': '9b498c08113f1e09617a1703c22b2f32',
        'followers': 'c76146de99bb02f6415203be841dd25a'
    }

    def __init__(self, login, password, tag_list, users_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.tag_list = tag_list
        self.users_list = users_list
        super(InstagramSpider, self).__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
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
                # for tag in self.tag_list:
                #     yield response.follow(f'/explore/tags/{tag}', callback=self.tag_parse)
                for user in self.users_list:
                    yield response.follow(f'/{user}', callback=self.user_parse)

    def user_parse(self, response):
        data = self.js_data_extract(response)
        user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
        print(1)
        yield InstagramUser(
            date_parse=datetime.datetime.now(),
            data=user_data,
            type='user'
        )
        yield from self.get_followed_api_request(response, user_data)

    def get_followed_api_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100
            }
        url = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_followed_api, cb_kwargs={'user_data': user_data})

    def get_followed_api(self, response, user_data):
        data = response.json()
        print(1)
        if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            variables = {
                'id': user_data['id'],
                'first': 100,
                'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor']
            }
            yield from self.get_followed_api_request(response, user_data, variables)

    def followers_parse(self, response):
        data = self.js_data_extract(response)
        print(3)

    def tag_parse(self, response):
        data = self.js_data_extract(response)
        tag_page = data['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield from self.get_tag(response, tag_page)

    def get_tag(self, response, tag_page):
        yield InstagramTag(date_parse=datetime.datetime.now(),
                           data={
                               'id': tag_page['id'],
                               'name': tag_page['name'],
                               'url': response.url,
                               'profile_pic_url': tag_page['profile_pic_url']
                           },
                           type='tag'
                           )

        yield from self.get_post(response, tag_page)

    def tag_api_parse(self, response):
        yield from self.get_post(response, response.json()['data']['hashtag'])

    def get_post(self, response, tag_page):
        if tag_page['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag_page['name'],
                'first': 100,
                'after': tag_page['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
            yield response.follow(
                url,
                callback=self.tag_api_parse,
            )

        yield from self.get_post_item(tag_page['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for node in edges:
            yield InstagramPost(
                date_parse=datetime.datetime.now(),
                data=node['node'],
                type='post'
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])
