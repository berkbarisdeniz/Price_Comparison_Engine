from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

class DermodrSpider(Spider):
    name = "dermodr"
    allowed_domains = ["dermodr.com"]
    start_urls = ["https://www.dermodr.com/"]
    
    def parse(self, response):
        main_categories = list(set(response.css('a.d-flex.align-items-center.w-100.menu-first-title::attr(href)').getall()))

        
        for link in main_categories:
            yield response.follow(link, self.parse_category_once)
    
    def parse_category_once(self, response):
        # Her ana kategori için sadece 1 çıktı:
        yield {
            'url': response.url,
        }

process = CrawlerProcess(settings={
    "FEEDS": {
        "categories_dermodr.json": {"format": "json"},
    },
    "LOG_LEVEL": "ERROR",
})

process.crawl(DermodrSpider)
process.start()
