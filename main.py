import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
from mutual_friends import MutualFriends
from handshakes import Handshakes, HandshakesChain

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
    handshakes_chain_proc = HandshakesChain()

    while True:
        crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'),
                         users_list=users_list[layer], layer=layer)
        crawl_proc.start()
        mutual_names_list = mutual_proc.run(users_list[layer], layer)
        handshakes_list = handshakes_proc.run(users_list[layer], layer)
        # handshakes_list = True
        if handshakes_list:
            chain_list = handshakes_chain_proc.run(handshakes_list, layer)
            break
        else:
            layer += 1
            users_list.append(mutual_names_list)
            print('ОШИБКА!!!')

    for i, block in enumerate(chain_list):
        print(f'{i + 1}. {block}')