import logging

from pymongo import MongoClient
from scrapy import signals
from scrapy.exceptions import NotConfigured


class SearchQueriesMongoDB:

    def __init__(self, mongodb_uri, database, collection):
        self.database = database
        self.collection = collection
        self.mongodb_uri = mongodb_uri
        self.logger = logging.getLogger('search-queries-mongodb')

    @classmethod
    def from_crawler(cls, crawler):

        mongodb_uri = crawler.settings.get('SEARCH_QUERIES_MONGODB_URI') or crawler.settings.get('MONGODB_URI')
        database = crawler.settings.get('SEARCH_QUERIES_DATABASE') or crawler.settings.get('MONGODB_DATABASE')
        collection = crawler.settings.get('SEARCH_QUERIES_COLLECTION')

        if not all([mongodb_uri, database, collection]):
            raise NotConfigured

        extension = cls(mongodb_uri, database, collection)
        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        return extension

    def spider_opened(self, spider):
        client = MongoClient(self.mongodb_uri)
        collection = client[self.database][self.collection]
        search_queries = collection.aggregate([{'$project': {'_id': 0}}, {'$sort': {'query': 1}}])
        search_queries = list(search_queries)
        spider.search_queries = search_queries
        self.logger.info(f'Loaded {len(search_queries)} search queries')
        client.close()
