import re
import datetime
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoYoulaItem, HhRemoteItem, InstagramItem


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

def get_tag_data(tag_page):
    tag_data_dict = {
        'id': '',
        'name': '',
        'allow_following': '',
        'is_following': '',
        'is_top_media_only': '',
        'profile_pic_url': ''
    }
    for key, value in tag_page.items():
        if key in tag_data_dict.keys():
            tag_data_dict[key] = value
    return tag_data_dict


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
    url_out = TakeFirst()
    default_item_class = HhRemoteItem
    title_out = TakeFirst()
    name_in = ''.join
    name_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    employer_url_out = list_to_str
    ext_url_out = TakeFirst()
    areas_of_activity_out = TakeFirst()
    employer_description_out = ''.join


# class InstagramLoader(ItemLoader):
#     date_parse_out = datetime.datetime.now()
#     tag_data_in = MapCompose(get_tag_data)
#     tag_data_out = TakeFirst()
#     post_data_out = TakeFirst()
    # id_out = TakeFirst()
    # name_out = TakeFirst()
    # allow_following = TakeFirst()
    # is_following = TakeFirst()
    # is_top_media_only = TakeFirst()
    # profile_pic_url = TakeFirst()
