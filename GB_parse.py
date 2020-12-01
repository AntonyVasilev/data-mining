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

import requests
import bs4
from urllib.parse import urljoin


class GBBlogParse:

    def __init__(self, start_url):
        self.start_url = start_url
        self.page_done = set()
        self.params = {
            'user-agent': 'Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 86.0.4240.198 Safari / 537.36'
        }

    def _get(self, url) -> bs4.BeautifulSoup:
        response = requests.get(url, params=self.params)
        self.page_done.add(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self._get(url)
            posts, pagination = self.params(soup)
            for post_url in posts:
                page_data = self.page_parse(self._get(post_url), post_url)

    def parse(self, soup):
        pag_ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, p_url.get('href')) for p_url in pag_ul.find_all('a') if p_url.get('href')
        )
        posts_wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts = set(
            urljoin(self.start_url, post_url.get('href')) for post_url in
            posts_wrapper.find_all('a', attrs={'class': 'post-items-title'})
        )

        return posts, paginations

    def page_parse(self, soup, url):
        pass


if __name__ == '__main__':
    parser = GBBlogParse('https://geekbrains.ru/posts')
    parser.run()