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
        'employer_url': '//a[@data-qa="vacancy-company-name"]/@href'
    }

    xpath_employer = {
        'name': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'ext_url': '//a[contains(@data-qa, "company-site")]/@href',
        'areas_of_activity': '//div[contains(@class, "employer-sidebar-block")]/p/text()',
        'employer_description': '//div[contains(@data-qa, "company-description")]//text()'
    }

    xpath_employer_mark = {
        'name': '//h1[@class=" "]/text()',
        'ext_url': '//div[contains(@class, "tmpl_hh_header")]//a[@target="_blank]"/@href',
        'employer_description': '//div[@class="hh37b__about__wrapper"]//text()'
    }

    xpath_employer_gp = {
        'name': '//title/text()',
        'ext_url': '//div[contains(@class, "tmpl_gazprom_logo")]//a[@target="_blank]"/@href',
        'employer_description': '//div[@class="tmpl_gazprom_content"]//text()'
    }

    xpath_employer_main = {
        'name': '//title/text()',
        'ext_url': '//div[contains(@class, "tmpl_hh_title")]//a[@target="_blank]"/@href',
        'employer_description': '//div[@class="tmpl_hh_banner__content"]//text()'
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
        yield response.follow(response.xpath(self.xpath_vacancy['employer_url']).get(), callback=self.employer_parse)

    def employer_parse(self, response):
        print(1)
        loader = HhRemoteLoader(response=response)
        loader.add_value('url', response.url)

        if response.url[-4:] == 'MARK':
            for key, value in self.xpath_employer_mark.items():
                loader.add_xpath(key, value)
        elif response.url[-4:] == 'main':
            for key, value in self.xpath_employer_main.items():
                loader.add_xpath(key, value)
        elif response.url[-4:] == '39305?dpt=gpn-39305-HOLD':
            for key, value in self.xpath_employer_gp.items():
                loader.add_xpath(key, value)
        else:
            for key, value in self.xpath_employer.items():
                loader.add_xpath(key, value)

        yield loader.load_item()
        yield response.follow(
            response.xpath('//a[contains(@data-qa, "employer-page__employer-vacancies-link")]/@href').get(),
            callback=self.parse)
