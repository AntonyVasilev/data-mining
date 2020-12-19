import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
from mutual_friends import MutualFriends

import dotenv

dotenv.load_dotenv('.env')

if __name__ == '__main__':
    users_list = ['mr.proghammer', 'codeforgeyt']
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    while True:
        crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'),
                         users_list=users_list)
        crawl_proc.start()
        mutual_proc = MutualFriends()
        handshakes, mutual_friends_list = mutual_proc.run(users_list)
        if handshakes:
            break
        else:
            users_list.clear()
            for mutual_friends in mutual_friends_list:
                for value in mutual_friends.values():
                    users_list.append(value)

    print(users_list, handshakes)
