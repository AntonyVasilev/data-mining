import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
from urllib.parse import urljoin

dotenv.load_dotenv('.env')


class MagnitParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0'
    }

    def __init__(self, start_url):
        self.start_url = start_url
        client = pymongo.MongoClient(os.getenv('DATA_BASE'))
        self.db = client['parse_les2']

        self.months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                       'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                       'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
                       }

        self.product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            'old_price': lambda soup: self._get_price(soup, 'old'),
            'new_price': lambda soup: self._get_price(soup, 'new'),
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            'date_from': lambda soup: self._get_dates(soup, 'from'),
            'date_to': lambda soup: self._get_dates(soup, 'to')
        }

    @staticmethod
    def _get_price(soup, price_type):
        if price_type == 'old':
            response = soup.find('div', attrs={'class': 'label__price_old'})
        elif price_type == 'new':
            response = soup.find('div', attrs={'class': 'label__price_new'})
        else:
            return
        return float(f'{response.contents[1].text}.{response.contents[3].text}')

    def _get_dates(self, soup, date_type):
        response = soup.find('div', attrs={'class': 'card-sale__date'})
        if date_type == 'from':
            date = response.contents[1].text[2:4]
            month = self.months[response.contents[1].text[5:]]
        elif date_type == 'to':
            date = response.contents[3].text[3:5]
            month = self.months[response.contents[3].text[6:]]
        year = dt.datetime.now().year
        return dt.datetime.strptime(f'{date}/{month}/{year}', '%d/%m/%Y')

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            pr_data = self.get_product(product)
            yield pr_data

    def get_product(self, product_soup) -> dict:

        result = {}
        for key, value in self.product_template.items():
            try:
                result[key] = value(product_soup)
            except Exception as e:
                continue
        return result

    def save(self, product):
        collection = self.db['test_parse_1']
        collection.insert_one(product)


if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()
