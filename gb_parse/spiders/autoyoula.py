import scrapy
import pymongo


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
            'author': '',
            'specification': self._get_specification(response),
        }
        print(1)

        # self.db.insert_one(data)

    def _get_specification(self, response):
        specification = response.css(
                    'div.AdvertCard_specs__2FEHc div.AdvertSpecs_row__ljPcX div.AdvertSpecs_data__xK2Qx')

        spec_dict = {}
        for feature in specification:
            spec_dict[feature.attrib.get('data-target')] = feature

        return {'year': int(spec_dict['advert-info-year'].css('a::text').get()),
                'mileage': spec_dict['advert-info-mileage'].css('::text').get(),
                'condition': spec_dict['advert-info-isCrashed'].css('::text').get(),
                'body_type': spec_dict['advert-info-bodyType'].css('a::text').get(),
                'transmission': spec_dict['advert-info-transmission'].css('::text').get(),
                'engine': spec_dict['advert-info-engineInfo'].css('::text').get(),
                'steering_wheel': spec_dict['advert-info-wheelType'].css('::text').get(),
                'colour': spec_dict['advert-info-color'].css('::text').get(),
                'drive_type': spec_dict['advert-info-driveType'].css('::text').get(),
                'engine_power': spec_dict['advert-info-enginePower'].css('::text').get(),
                'is_customs_cleared': spec_dict['advert-info-isCustom'].css('::text').get(),
                'number_of_owners': int(spec_dict['advert-info-owners'].css('::text').get())
            }
