from datetime import datetime
import re
from itertools import product
from urllib.parse import urlencode

import dateparser
from scrapy import Spider, Request
from w3lib.html import remove_tags, replace_entities
from w3lib.url import url_query_cleaner


CHROME_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 ' \
                    'Safari/537.36 '

# Search Settings
SEARCH_QUERIES = ['Scrapy', 'Python', 'Django', 'Scraping', 'Brandquad', 'Scrapy Developer']
SEARCH_REGIONS = ['Moscow', 'Saint-Petersburg', 'Volgograd']

# Regions settings
REGIONS_SETTINGS = {
    'Moscow': {'domain': 'hh.ru', 'city_id': 1},
    'Saint-Petersburg': {'domain': 'spb.hh.ru', 'city_id': 2},
    'Volgograd': {'domain': 'volgograd.hh.ru', 'city_id': 24},
}

# Regex
SALARY_REGEX = re.compile(r'(от(?P<minimum>\d+))?(до(?P<maximum>\d+))?', re.IGNORECASE)
CREATED_AT_REGEX = re.compile(r'\d{1,2}\s+\w+\s+\d{4}')


class HeadHunterSpider(Spider):
    name = 'headhunter'
    user_agent = CHROME_USER_AGENT
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,
        'MONGODB_UNIQUE_KEY': 'offer_id',
        'PYDANTIC_MODEL': 'midas.serializers.Offer',
        'ITEM_PIPELINES': {
            'midas.pipelines.DuplicatesOfferPipeline': 300,
            'midas.pipelines.PydanticPipeline': 325,
            'scrapy_mongodb.MongoDBPipeline': 350,
        },
    }

    def start_requests(self):
        for query, region in product(SEARCH_QUERIES, SEARCH_REGIONS):
            yield Request(url=self.build_search_url(query=query, region=region), callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//div[has-class("vacancy-serp-item")]//a[contains(@href, "/vacancy/")]/@href')
        yield from response.follow_all(urls=urls, callback=self.parse_vacancy)

        # Pagination
        next_page = response.xpath('//div[@data-qa="pager-block"]//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_vacancy(self, response):
        vacancy_id = response.xpath('//input[@name="vacancyId"]/@value').get()
        vacancy_id = vacancy_id or url_query_cleaner(response.url).rstrip('/').rpartition('/')[-1]

        tags = response.xpath('//div[@class="bloko-tag-list"]//span/text()').getall()
        tags = [tag.strip().lower() for tag in tags if tag.strip()]

        created_at = remove_tags(response.xpath('//p[has-class("vacancy-creation-time")]').get(''))
        created_at = CREATED_AT_REGEX.search(created_at.replace('\xa0', ' '))
        created_at = dateparser.parse(created_at.group()) if created_at else None

        yield {
            'offer_id': int(vacancy_id),
            'title': remove_tags(response.xpath('//h1[@data-qa="vacancy-title"]').get('')),
            'url': url_query_cleaner(response.url),
            'company': self.get_company_info(response),
            'city': response.xpath('//p[@data-qa="vacancy-view-location"]/text()').get(''),
            'salary': self.get_salary(response),
            'info': self.get_offer_info(response),
            'created_at': created_at,
            'tags': tags,
        }

    @staticmethod
    def build_search_url(query: str, region: str = 'Moscow') -> str:
        region = REGIONS_SETTINGS[region]
        params = {
            'clusters': True,
            'area': region['city_id'],
            'st': 'searchVacancy',
            'text': query,
            'customDomain': 1,
        }
        query = urlencode(params, doseq=True)
        return f'https://{region["domain"]}/search/vacancy?{query}'

    @staticmethod
    def get_salary(response):
        salary = remove_tags(response.xpath('//p[has-class("vacancy-salary")]').get(''))
        salary = salary.replace('\xa0', '').replace(' ', '').lower()
        salary = SALARY_REGEX.search(salary).groupdict(default='0')
        salary['maximum'] = float(salary['maximum'])
        salary['minimum'] = float(salary['minimum'])
        salary['value'] = max(salary['minimum'], salary['maximum'])
        return salary

    @staticmethod
    def get_company_info(response):
        company = response.xpath('//a[has-class("vacancy-company-name")]')
        return {
            'name': remove_tags(company.xpath('./*').get()),
            'url': response.urljoin(company.xpath('./@href').get())
        }

    @staticmethod
    def get_offer_info(response):
        description = remove_tags(response.xpath('//div[@data-qa="vacancy-description"]').get('')).strip()
        address = remove_tags(response.xpath('//span[@data-qa="vacancy-view-raw-address"]').get('')).strip()
        return {'description': description, 'address': address}
