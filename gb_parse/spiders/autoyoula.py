import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_gb'][self.name]

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,
            'author': self._get_author(response),
            'specification': self._get_specification(response),
        }
        self.db.insert_one(data)

    @staticmethod
    def _get_specification(response):
        specification = response.css(
            'div.AdvertCard_specs__2FEHc div.AdvertSpecs_row__ljPcX div.AdvertSpecs_data__xK2Qx')

        data = {'year': int(specification.css('[data-target="advert-info-year"] a::text').get()) if
                specification.css('[data-target="advert-info-year"] a::text').get() else None,
                'mileage': specification.css('[data-target="advert-info-mileage"]::text').get() or None,
                'body_type': specification.css('[data-target="advert-info-bodyType"] a::text').get() or None,
                'transmission': specification.css('[data-target="advert-info-transmission"]::text').get() or None,
                'engine': specification.css('[data-target="advert-info-engineInfo"]::text').get() or None,
                'steering_wheel': specification.css('[data-target="advert-info-wheelType"]::text').get() or None,
                'colour': specification.css('[data-target="advert-info-color"]::text').get() or None,
                'drive_type': specification.css('[data-target="advert-info-driveType"]::text').get() or None,
                'engine_power': specification.css('[data-target="advert-info-enginePower"]::text').get() or None,
                'is_customs_cleared': specification.css('[data-target="advert-info-isCustom"]::text').get() or None,
                'number_of_owners': int(specification.css('[data-target="advert-info-owners"]::text').get()) if
                specification.css('[data-target="advert-info-owners"]::text').get() else None
                }
        return data

    @staticmethod
    def _get_author(response):
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None
