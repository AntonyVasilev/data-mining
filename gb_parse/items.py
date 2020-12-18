# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AutoYoulaItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    specifications = scrapy.Field()


class HhRemoteItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    employer_url = scrapy.Field()
    ext_url = scrapy.Field()
    areas_of_activity = scrapy.Field()
    employer_description = scrapy.Field()


class InstagramMutual(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    mutual_follow = scrapy.Field()


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    # type = scrapy.Field()


class InstagramTag(InstagramItem):
    pass


class InstagramPost(InstagramItem):
    pass


class InstagramUser(InstagramItem):
    pass


class InstagramFollow(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    follow_name = scrapy.Field()
    follow_id = scrapy.Field()
    type = scrapy.Field()


class InstagramFollowed(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    followed_name = scrapy.Field()
    followed_id = scrapy.Field()
    type = scrapy.Field()
