import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
from pymongo import MongoClient

import dotenv
dotenv.load_dotenv('.env')

if __name__ == '__main__':
    users_list = ['mr.proghammer', 'codeforgeyt']
    # users_list = ['mr.proghammer', 'code__zone']
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'), users_list=users_list)
    crawl_proc.start()

    db = MongoClient()['parse_gb']
    collection = db['instagram']
    chain_data = collection.find_one({'type': 'chain'})
    print(f'\n\n\nThe shortest path between {chain_data["start_user_name"]} and {chain_data["target_user_name"]} is:')
    for i, user in enumerate(chain_data['handshakes_chain']):
        print(f'{i + 1}. {user}')
