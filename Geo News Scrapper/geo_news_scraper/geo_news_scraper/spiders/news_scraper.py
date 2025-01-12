import csv
from collections import OrderedDict
from datetime import datetime

from scrapy import Spider, Request


class NewsScraperSpider(Spider):
    name = "news_scraper"
    start_url = "https://www.geo.tv/"

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Opera GX";v="115", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_file = f'output/News {self.current_datetime}.csv'


    def start_requests(self):
        yield Request(url=self.start_url, headers=self.headers,
                      callback=self.parse)

    def parse(self, response, **kwargs):
        categories = response.css('.header_bottom .open-section ::attr(href)').getall()

        for category in categories:
            yield Request(url=category, headers=self.headers,
                          callback=self.parse_categories)

    def parse_categories(self, response):
        news_urls = list(set(response.css('.video-list[data-vr-zone*="Page"] [data-vr-contentbox-url*="https"] ::attr(href)').getall()))

        for news_url in news_urls:
            yield Request(url=news_url, headers=self.headers,
                          callback=self.parse_details)

    def parse_details(self, response):
        item = OrderedDict()

        item['Category'] = ' > '.join(response.css('.breadcrumb a::text').getall()).strip()
        item['Title'] = response.css('.heading_H ::text').get('').strip()
        item['Post Time'] = response.css('.post-date-time ::text').get('').strip()
        item['Author'] = response.css('.author_agency ::text').get('').strip()
        item['Detail'] = '\n'.join(response.css('.content-area *:not(style):not(script):not(figure)::text').getall()).strip()

        self.write_to_csv(item)
        yield item

    def write_to_csv(self, data):
        headers = ['Category', 'Title', 'Post Time', 'Author', 'Detail']

        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)

            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow(data)
