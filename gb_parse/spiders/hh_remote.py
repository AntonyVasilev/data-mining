import scrapy


class HhRemoteSpider(scrapy.Spider):
    name = 'hh_remote'
    allowed_domains = ['https://hh.ru/search/vacancy?schedule=remote']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/']

    xpath_query = {
        'pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "bloko-button HH-Pager-Control")]'
    }

    def parse(self, response):
        for pag_page in response.xpath(self.xpath_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.parse)
