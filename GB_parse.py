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
import bs4
import requests
from urllib.parse import urljoin
from database import GBDataBase


class GbBlogParse:

    def __init__(self, start_url):
        self.start_url = start_url
        self.page_done = set()
        self.db = GBDataBase('sqlite:///gb_blog.db')

    def _get(self, url):
        response = requests.get(url)
        # todo Обработка статусов и ошибки
        self.page_done.add(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self._get(url)
            posts, pagination = self.parse(soup)
            for post_url in posts:
                page_data = self.page_parse(self._get(post_url), post_url)
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

    def page_parse(self, soup, url) -> dict:
        return {
            'url': url,
            'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            'img_url': '',
            'post_date': '',
            'writer': {
                'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                'url': urljoin(self.start_url, soup.find('div', attrs={'itemprop': 'author'}).parent.get('href'))
            },
            'comment': {
                'author_name': '',
                'author_url': '',
                'text': ''
            },
            'tags': []
        }

    def save(self, post_data: dict):
        self.db.create_post(post_data)


if __name__ == '__main__':
    parser = GbBlogParse('https://geekbrains.ru/posts')
    parser.run()
