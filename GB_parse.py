"""
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
список тегов
"""

from typing import Tuple, Set
import time
import bs4
import requests
from urllib.parse import urljoin
import datetime as dt
from database import GBDataBase


class GbBlogParse:

    def __init__(self, start_url):
        self.start_url = start_url
        self.page_done = set()
        self.db = GBDataBase('sqlite:///gb_blog.db')

        self.months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,'мая': 5, 'июня': 6,
            'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }

    def _get(self, url):
        while True:
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    raise Exception
                self.page_done.add(url)
                return bs4.BeautifulSoup(response.text, 'lxml')
            except Exception:
                time.sleep(0.5)

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self._get(url)
            posts, pagination = self.parse(soup)
            for post_url in posts:
                page_data = self.page_parse(self._get(post_url), post_url)
                print(1)
                self.save(page_data)

            for pag_url in pagination:
                self.run(pag_url)

    def parse(self, soup) -> Tuple[Set[str], Set[str]]:
        pag_ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, p_url.get('href')) for p_url in pag_ul.find_all('a') if p_url.get('href')
        )
        posts_wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})

        posts = set(
            urljoin(self.start_url, post_url.get('href')) for post_url in
            posts_wrapper.find_all('a', attrs={'class': 'post-item__title'})
        )

        return posts, paginations

    def _get_date(self, soup):
        date = soup.find('time', attrs={'class': 'text-md'}).text
        day, text_month, year = date.split(' ')
        month = self.months[text_month]
        return dt.datetime(int(year), month, int(day))

    def _get_tag(self, soup):
        tags_list = []
        for tag in soup.find_all('a', attrs={'class': 'small'}):
            tag_dict = {}
            tag_dict['url']  = urljoin(self.start_url, tag.get('href'))
            tag_dict['name'] = tag.text
            tags_list.append(tag_dict)
        return tags_list

    def page_parse(self, soup, url) -> dict:
        response = {
            'url': url,
            'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            'img_url': soup.find('div', attrs={'class': 'blogpost-content'}).find('img').get('src'),
            'post_date': self._get_date(soup),
            'writer': {
                'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                'url': urljoin(self.start_url, soup.find('div', attrs={'itemprop': 'author'}).parent.get('href'))
            },
            # 'comment': {
            #     'author_name': '',
            #     'author_url': '',
            #     'text': ''
            # },
            'tags': self._get_tag(soup)
        }
        print(1)
        return response

    def save(self, post_data: dict):
        self.db.create_post(post_data)


if __name__ == '__main__':
    parser = GbBlogParse('https://geekbrains.ru/posts')
    parser.run()
