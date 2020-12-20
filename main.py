import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
from mutual_friends import MutualFriends
from handshakes import Handshakes

import dotenv

dotenv.load_dotenv('.env')

if __name__ == '__main__':
    start_users_list = ['mr.proghammer', 'codeforgeyt']

    layer = 0
    users_list = [[[start_users_list[0]], [start_users_list[1]]], ]

    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    mutual_proc = MutualFriends()
    handshakes_proc = Handshakes()

    while True:
        crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'),
                         users_list=users_list[layer], layer=layer)
        crawl_proc.start()
        # mutual_proc.run(users_list[layer], layer)
        # has_handshakes = handshakes_proc.run(users_list[layer], layer)
        # has_handshakes = True
        # if has_handshakes:
        #     break
        # else:
        #     layer += 1
    # print(users_list)
