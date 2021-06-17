import re
import scrapy
from ..loaders import AutoYoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    db_type = 'MONGO'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    itm_template = {
        'title': '//div[@data-target="advert-title"]/text()',
        'images': '//figure[contains(@class, "PhotoGallery_photo")]//img/@src',
        'description': '//div[contains(@class, "AdvertCard_descriptionInner")]//text()',
        'author': '//script[contains(text(), "window.transitState =")]/text()',
        'specifications':
            '//div[contains(@class, "AdvertCard_specs")]/div/div[contains(@class, "AdvertSpecs_row")]',
    }

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        loader = AutoYoulaLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.itm_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()
