from datetime import datetime
import re
from urllib.parse import urlencode

from scrapy import Spider, Request
from w3lib.html import remove_tags, replace_entities
from w3lib.url import url_query_cleaner

CHROME_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 ' \
                    'Safari/537.36 '


# Поисковые запросы
SEARCH_QUERIES = ['Scrapy', 'Python', 'Django', 'Scraping', 'Brandquad', 'Scrapy Developer']


# Regex
SALARY_REGEX = re.compile(r'(от(?P<minimum>\d+))?(до(?P<maximum>\d+))?', re.IGNORECASE)


class HeadHunterSpider(Spider):
    name = 'headhunter'
    user_agent = CHROME_USER_AGENT
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,
        'MONGODB_UNIQUE_KEY': 'vacancy_id',
        'SPIDERMON_VALIDATION_MODELS': (
            'midas.validators.HeadHunterItem',
        ),
    }

    def start_requests(self):
        for query in SEARCH_QUERIES:
            yield Request(url=self.build_search_url(query=query), callback=self.parse)

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
        yield {
            'timestamp': int(datetime.now().timestamp()),
            'vacancy_id': int(vacancy_id),
            'title': remove_tags(response.xpath('//h1[@data-qa="vacancy-title"]').get('')),
            'url': url_query_cleaner(response.url),
            'company': self.get_company_info(response),
            'salary': self.get_salary(response),
            # 'meta': self.get_meta(response),
        }

    @staticmethod
    def build_search_url(query: str, city_id: int = 1) -> str:
        params = {
            'clusters': True,
            'area': city_id,
            'st': 'searchVacancy',
            'text': query,
            'customDomain': 1,
        }
        query = urlencode(params, doseq=True)
        return f'https://hh.ru/search/vacancy?{query}'

    @staticmethod
    def get_salary(response):
        salary_str = remove_tags(response.xpath('//p[has-class("vacancy-salary")]').get(''))
        salary_str = salary_str.replace('\xa0', '')
        salary_range = salary_str.replace(' ', '').lower()
        salary_range = SALARY_REGEX.search(salary_range).groupdict(default='0')
        return {'value': salary_str, 'range': salary_range}

    @staticmethod
    def get_meta(response):
        pass

    @staticmethod
    def get_company_info(response):
        company = response.xpath('//a[has-class("vacancy-company-name")]')
        if company:
            return {
                'name': remove_tags(company.xpath('./*').get()),
                'url': response.urljoin(company.xpath('./@href').get())
            }
        return {'name': '', 'url': ''}
