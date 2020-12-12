import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoYoulaItem, HhRemoteItem


def get_author(js_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, js_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


def get_specifications(itm):
    tag = Selector(text=itm)
    result = {tag.css('.AdvertSpecs_label__2JHnS::text').get(): tag.css(
        '.AdvertSpecs_data__xK2Qx::text').get() or tag.css('a::text').get()}
    return result


def specifications_out(data: list):
    result = {}
    for itm in data:
        result.update(itm)
    return result


def list_to_str(list_in):
    result = ''
    for el in list_in:
        result += el
    return result

# def add_or_none(data):
#     return data if data else None


class AutoYoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_out = TakeFirst()
    author_in = MapCompose(get_author)
    author_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = specifications_out


class HhRemoteLoader(ItemLoader):
    default_item_class = HhRemoteItem
    title_out = TakeFirst()
    name_in = ''.join
    name_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    author_url_out = list_to_str
    ext_url_out = TakeFirst()
    # areas_of_activity_in = add_or_none
    areas_of_activity_out = TakeFirst()
    # author_description_in = add_or_none
    author_description_out = ''.join
