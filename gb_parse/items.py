# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramMutual(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    mutual_follow = scrapy.Field()


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()


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
    layer = scrapy.Field()
    edge = scrapy.Field()
    has_mutual = scrapy.Field()


class InstagramFollowed(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    followed_name = scrapy.Field()
    followed_id = scrapy.Field()
    type = scrapy.Field()
    layer = scrapy.Field()
    edge = scrapy.Field()
    has_mutual = scrapy.Field()


class InstagramUsers(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    type = scrapy.Field()


class InstagramChain(scrapy.Item):
    _id = scrapy.Field()
    start_user_name = scrapy.Field()
    target_user_name = scrapy.Field()
    handshakes_chain = scrapy.Field()
    type = scrapy.Field()
