import scrapy
from ..loaders import HhRemoteLoader


class HhRemoteSpider(scrapy.Spider):
    name = 'hh_remote'
    db_type = 'MONGO'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/']

    xpath_query = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'vacancy': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
    }

    xpath_vacancy = {
        'title': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        'description': '//div[@data-qa="vacancy-description"]//p//text()',
        'skills': '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        'author_url': '//a[@data-qa="vacancy-company-name"]/@href'
    }

    xpath_author = {
        'name': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'ext_url': '//a[contains(@data-qa, "company-site")]/@href',
        'areas_of_activity': '//div[contains(@class, "employer-sidebar-block")]/p/text()',
        'author_description': '//div[contains(@data-qa, "company-description")]//text()'
    }

    xpath_author_mark = {
        'name': '//h1[@class="hh37b_head_wrapper_title"]/text()',
        'ext_url': '//div[contains(@class, "tmpl_hh_header")]//a[@target="_blank]"/@href',
        'author_description': '//div[@class="hh37b__about__wrapper"]//text()'
    }

    xpath_author_gp = {
        'name': '//title/text()',
        'ext_url': '//div[contains(@class, "tmpl_gazprom_logo")]//a[@target="_blank]"/@href',
        'author_description': '//div[@class="tmpl_gazprom_content"]//text()'
    }

    def parse(self, response, **kwargs):
        for pag_page in response.xpath(self.xpath_query['pagination']):
            yield response.follow(pag_page, callback=self.parse)

        for vacancy in response.xpath(self.xpath_query['vacancy']):
            yield response.follow(vacancy, callback=self.vacancy_parse)

    def vacancy_parse(self, response):
        loader = HhRemoteLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self.xpath_vacancy.items():
            loader.add_xpath(key, value)

        yield loader.load_item()

        if response.xpath(self.xpath_vacancy['author_url']).get()[-4:] == 'MARK':
            yield response.follow(response.xpath(self.xpath_vacancy['author_url']).get(),
                                  callback=self.mark_author_parse)
        elif response.xpath(self.xpath_vacancy['author_url']).get()[-4:] == '39305?dpt=gpn-39305-HOLD':
            yield response.follow(response.xpath(self.xpath_vacancy['author_url']).get(),
                                  callback=self.gp_author_parse)
        else:
            yield response.follow(response.xpath(self.xpath_vacancy['author_url']).get(), callback=self.author_parse)

    def author_parse(self, response):
        loader = HhRemoteLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self.xpath_author.items():
            loader.add_xpath(key, value)

        yield loader.load_item()

    def mark_author_parse(self, response):
        loader = HhRemoteLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self.xpath_author_mark.items():
            loader.add_xpath(key, value)

        yield loader.load_item()

    def gp_author_parse(self, response):
        loader = HhRemoteLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self.xpath_author_gp.items():
            loader.add_xpath(key, value)

        yield loader.load_item()