import os
from pathlib import Path
import json
import time
import requests


class WrongStatusCode(Exception):
    """
    Класс-исключение для обработки ситуации, когда при GET запросе возвращается код, отличный от 200
    """
    pass


class Parse5ka:
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    _params = {
        'records_per_page': 50
    }

    def __init__(self, start_url, cat_url):
        self.start_url = start_url
        self.cat_url = cat_url

    @staticmethod
    def _get(*args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise WrongStatusCode
                return response
            except WrongStatusCode:
                time.sleep(0.25)

    def parse(self, url, param_cat):
        params = self._params
        while url:
            params['categories'] = param_cat
            response: requests.Response = self._get(url, params=params, headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')
            yield data.get('results')

    def _get_categories(self, url):
        params = self._params
        response = requests.get(url, params=params, headers=self._headers)
        return json.loads(response.text)

    def run(self):
        prods_list = []
        categories = self._get_categories(self.cat_url)
        for category in categories:
            category_dict = category
            for products in self.parse(self.start_url, category["parent_group_code"]):
                prods_list = [product for product in products]
                time.sleep(0.1)
            category_dict['products'] = prods_list
            self._save_to_file(category_dict)
            prods_list.clear()

    @staticmethod
    def _save_to_file(category_dict):
        path = Path(os.path.dirname(__file__)).joinpath('products').joinpath(f'{category_dict["parent_group_code"]}.json')
        with open(path, 'w', encoding='UTF-8') as file:
            json.dump(category_dict, file, ensure_ascii=False)


if __name__ == '__main__':
    url_start = 'https://5ka.ru/api/v2/special_offers/'
    url_categories = 'https://5ka.ru/api/v2/categories/'
    parser = Parse5ka(url_start, url_categories)
    parser.run()
