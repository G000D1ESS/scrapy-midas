from datetime import datetime
from urllib.parse import urlencode

import extruct
from scrapy import Spider, Request
from w3lib.html import remove_tags
from w3lib.url import url_query_cleaner


CHROME_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 ' \
                    'Safari/537.36 '

# Search Settings
SEARCH_QUERIES = ['Scrapy', 'Python', 'Django', 'Scraping', 'Brandquad', 'Scrapy Developer']


class HabrCareerSpider(Spider):
    name = 'habrcareer'
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
        for query in SEARCH_QUERIES:
            yield Request(url=self.build_search_url(query=query), callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//div[has-class("vacancy-card")]//a[contains(@href, "/vacancies/")]/@href')
        yield from response.follow_all(urls=urls, callback=self.parse_offer)

        # Pagination
        next_page = response.xpath('//a[has-class("next_page")]/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_offer(self, response):
        page_data = extruct.extract(response.text)
        offer_data = next(item for item in page_data['json-ld'] if item.get('@type') == 'JobPosting')

        city = offer_data['jobLocation']
        if isinstance(city, list):
            city = next(item['address'] for item in city if item.get('@type') == 'Place')
        elif isinstance(city, dict):
            city = city['address']
            city = city.get('addressLocality', '') if isinstance(city, dict) else city
        else:
            city = ''
        city = str(city).strip().title()

        tags = response.xpath('//h2[@class="content-section__title" and contains(text(),"навыки")]')
        tags = tags.xpath('./../../span[@class="preserve-line"]').getall()
        tags = [remove_tags(tag).lower().strip() for tag in tags]

        yield {
            'offer_id': int(offer_data['identifier']['value']),
            'title': offer_data['title'],
            'url': url_query_cleaner(response.url),
            'company': self.get_company_info(response),
            'city': city,
            'salary': self.get_salary(offer_data),
            'info': self.get_offer_info(offer_data),
            'created_at': datetime.strptime(offer_data['datePosted'], '%Y-%m-%d'),
            'tags': tags,
        }

    @staticmethod
    def build_search_url(query: str) -> str:
        params = {'q': query, 'l': 1, 'type': 'all'}
        query = urlencode(params, doseq=True)
        return f'https://career.habr.com/vacancies?{query}'

    @staticmethod
    def get_salary(offer_data):
        if 'baseSalary' in offer_data:
            salary = dict()
            salary['maximum'] = float(offer_data['baseSalary']['value'].get('maxValue', 0))
            salary['minimum'] = float(offer_data['baseSalary']['value'].get('minValue', 0))
            salary['value'] = max(salary['minimum'], salary['maximum'])
            return salary
        return {'maximum': 0, 'minimum': 0, 'value': 0}

    @staticmethod
    def get_company_info(response):
        company = response.xpath('//div[has-class("company_name")]/a')
        return {
            'name': remove_tags(company.xpath('./text()').get()),
            'url': response.urljoin(company.xpath('./@href').get())
        }

    @staticmethod
    def get_offer_info(offer_data):
        return {'description': remove_tags(offer_data['description']).strip()}
