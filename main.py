import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider

import dotenv
dotenv.load_dotenv('.env')

if __name__ == '__main__':
    users_list = ['mr.proghammer', 'codeforgeyt']
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'), users_list=users_list)
    crawl_proc.start()
