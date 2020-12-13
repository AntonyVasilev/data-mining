"""
Задача авторизованным пользователем обойти список произвольных тегов,
Сохранить структуру Item олицетворяющую сам Tag (только информация о теге)

Сохранить структуру данных поста, Включая обход пагинации. (каждый пост как отдельный item, словарь внутри node)

Все структуры должны иметь след вид

date_parse (datetime) время когда произошло создание структуры
data - данные полученые от инстаграм
Скачать изображения всех постов и сохранить на диск
"""

import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32'
    }
    # {"tag_name": "python",
    #  "first": 5  ,
    #  "after": "QVFDTjZ6UDYxM245VW1BeEJLaHVtcGxwdldiS0dlYnlFRXpoc09uUzFPSDMxbC1ueGNpd0k5MzQ5Mk1jSFpla3hLVUo4b24zSWhFOXg5QVllemp5V1ctVg=="
    #  https://www.instagram.com/graphql/query/?query_hash=9b498c08113f1e09617a1703c22b2f32&variables=%7B%22tag_name%22%3A%22python%22%2C%22first%22%3A5%2C%22after%22%3A%22QVFDTjZ6UDYxM245VW1BeEJLaHVtcGxwdldiS0dlYnlFRXpoc09uUzFPSDMxbC1ueGNpd0k5MzQ5Mk1jSFpla3hLVUo4b24zSWhFOXg5QVllemp5V1ctVg%3D%3D%22%7D}

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
        print(1)

    def tag_parse(self, response):
        data = self.js_data_extract(response)
        print(1)

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])