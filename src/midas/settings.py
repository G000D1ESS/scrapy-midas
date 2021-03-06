import logging

from decouple import config

BOT_NAME = 'midas'

SPIDER_MODULES = ['midas.spiders']
NEWSPIDER_MODULE = 'midas.spiders'

# Configure logging levels
logging.getLogger('pymongo').setLevel('INFO')
logging.getLogger('requests').setLevel('INFO')


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'midas (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

FEED_EXPORT_ENCODING = 'utf-8'

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# MongoDB settings
MONGODB_URI = config('MONGODB_URI')
MONGODB_DATABASE = config('MONGODB_DATABASE')
MONGODB_SEPARATE_COLLECTIONS = True
MONGODB_ADD_TIMESTAMP = False

# Search Queries from MongoDB settings
SEARCH_QUERIES_MONGODB_URI = MONGODB_URI
SEARCH_QUERIES_DATABASE = MONGODB_DATABASE
SEARCH_QUERIES_COLLECTION = 'search_queries'

# SpiderMon settings
SPIDERMON_ENABLED = True
SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS = True
SPIDERMON_TELEGRAM_SENDER_TOKEN = config('TELEGRAM_SENDER_TOKEN')
SPIDERMON_TELEGRAM_RECIPIENTS = [config('TELEGRAM_RECIPIENTS')]
SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES = True
SPIDERMON_SPIDER_CLOSE_MONITORS = (
    'midas.monitors.SpiderCloseMonitorSuite',
)

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'midas.middlewares.MidasSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'midas.middlewares.MidasDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'midas.extensions.SearchQueriesMongoDB': 450,
    'spidermon.contrib.scrapy.extensions.Spidermon': 500,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     'scrapy_mongodb.MongoDBPipeline': 900,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
