from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from urllib.parse import urljoin

class MarkaFarmaSpider(Spider):
    name = "markafarma"
    allowed_domains = ["markafarma.com"]
    start_urls = ["https://www.markafarma.com/"]
    
    def parse(self, response):
        main_categories = list(set(response.css('a.d-flex.align-items-center.h-100.w-100.px-1.text-center.main-link::attr(href)').getall()))
        
        for link in main_categories:
            full_link = urljoin(self.start_urls[0], link)
            yield response.follow(full_link, self.parse_category_once)
    
    def parse_category_once(self, response):
        yield {
            'url': response.url,
        }

process = CrawlerProcess(settings={
    "FEEDS": {
        "categories_markafarma.json": {"format": "json"},
    },
    "LOG_LEVEL": "ERROR",
})

process.crawl(MarkaFarmaSpider)
process.start()