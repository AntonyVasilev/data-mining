"""
Задача авторизованным пользователем обойти список произвольных тегов,
Сохранить структуру Item олицетворяющую сам Tag (только информация о теге)

Сохранить структуру данных поста, Включая обход пагинации. (каждый пост как отдельный item, словарь внутри node)

Все структуры должны иметь след вид

date_parse (datetime) время когда произошло создание структуры
data - данные полученые от инстаграм
Скачать изображения всех постов и сохранить на диск
"""
import datetime
import json
import scrapy
from ..items import InstagramTag, InstagramPost


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    db_type = 'MONGO'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    api_url = '/graphql/query/'
    query_hash = {
        'tag_posts': '9b498c08113f1e09617a1703c22b2f32'
    }

    def __init__(self, login, password, tag_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.tag_list = tag_list
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
                for tag in self.tag_list:
                    yield response.follow(f'/explore/tags/{tag}', callback=self.tag_parse)

    def tag_parse(self, response):
        data = self.js_data_extract(response)
        tag_page = data['entry_data']['TagPage'][0]['graphql']['hashtag']
        print(1)
        yield from self.get_tag(response, tag_page)

    def get_tag(self, response, tag_page):
        yield InstagramTag(date_parse=datetime.datetime.now(),
                           data={
                               'id': tag_page['id'],
                               'name': tag_page['name'],
                               'url': response.url,
                               'profile_pic_url': tag_page['profile_pic_url']
                           },
                           type='post'
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
