from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

class DermoeczanemSpider(Spider):
    name = "dermoeczanem"
    allowed_domains = ["dermoeczanem.com"]
    start_urls = ["https://www.dermoeczanem.com/"]
    
    def parse(self, response):
        main_categories = list(set(response.css('a.d-flex.align-items-center.w-100.px-1.text-center.text-uppercase.menu-first-title::attr(href)').getall()))
        
        for link in main_categories:
            yield response.follow(link, self.parse_category_once)
    
    def parse_category_once(self, response):
        yield {
            'url': response.url,
        }

process = CrawlerProcess(settings={
    "FEEDS": {
        "categories_dermoeczanem.json": {"format": "json"},
    },
    "LOG_LEVEL": "ERROR",
})

process.crawl(DermoeczanemSpider)
process.start()