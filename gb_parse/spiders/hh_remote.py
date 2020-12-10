import scrapy


class HhRemoteSpider(scrapy.Spider):
    name = 'hh_remote'
    allowed_domains = ['hh.ru', 'nemchinovka.hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/']

    xpath_query = {
        'pagination': '//a[contains(@class, "HH-Pager-Control")]',
        'vacancy': '//a[contains(@class, "HH-VacancySidebarTrigger-Link")]',
        'author': '//a[contains(@class, "vacancy-company-name")]'
    }

    def parse(self, response):
        # for pag_page in response.xpath(self.xpath_query['pagination']):
        #     yield response.follow(pag_page.attrib.get('href'), callback=self.parse)

        for vacancy in response.xpath(self.xpath_query['vacancy']):
            yield response.follow(vacancy.attrib.get('href'), callback=self.vacancy_parse)

    def vacancy_parse(self, response):
        salary_text = ''
        for el in response.xpath('//p[contains(@class, "vacancy-salary")]/span/text()'):
            salary_text += el.get()

        vacancy = {
            'title': response.xpath('//h1[contains(@data-qa, "vacancy-title")]/text()').get(),
            'salary': self.__list_to_str(response.xpath(
                '//p[contains(@class, "vacancy-salary")]/span/text()').getall()),
            'description': self.__list_to_str(response.xpath(
                '//div[contains(@class, "vacancy-description")]//p//text()').getall()),
            'skills': response.xpath('//div[contains(@class, "bloko-tag-list")]//text()').getall(),
            'author_url': response.xpath('//a[contains(@class, "vacancy-company-name")]').attrib.get('href')
        }

        print(1)

        # response.follow(response.xpath('//a[contains(@class, "vacancy-company-name")]').attrib.get('href'), callback=self.author_parse)

        for author in response.xpath(self.xpath_query['author']):
            yield response.follow(author.attrib.get('href'), callback=self.author_parse)

    def author_parse(self, response):
        author = {
            'title': self.__list_to_str(response.xpath('//h1[contains(@class, "bloko-header-1")]//text()').getall()),
            'ext_url': response.xpath('//a[contains(@class, "g-user-content")]//@href').get() if
                response.xpath('//a[contains(@class, "g-user-content")]//@href').get() else None,
            'areas_of_activity': response.xpath(
                '//div[contains(@class, "employer-sidebar-block__header")]/following::p[1]/text()').getall() if
                response.xpath('//div[contains(@class, "employer-sidebar-block__header")]/following::p[1]/text()').getall()
                else None,
            'description': self.__list_to_str(
                response.xpath('//div[contains(@class, "g-user-content")]//text()').getall()) if
                response.xpath('//div[contains(@class, "g-user-content")]//text()').getall() else None
        }
        print(1)

    @staticmethod
    def __list_to_str(list_in):
        result = ''
        for el in list_in:
            result += el
        return result



