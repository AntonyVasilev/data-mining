import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hh_remote import HhRemoteSpider
from gb_parse.spiders.instagram import InstagramSpider

import dotenv

dotenv.load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # crawl_proc.crawl(AutoyoulaSpider)
    # crawl_proc.crawl(HhRemoteSpider)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'),
                     tag_list=['python', 'machinelearning', 'ai'])
    crawl_proc.start()
