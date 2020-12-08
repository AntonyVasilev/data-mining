from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hh_remote import HhRemoteSpider


if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # crawl_proc.crawl(AutoyoulaSpider)
    crawl_proc.crawl(HhRemoteSpider)
    crawl_proc.start()
