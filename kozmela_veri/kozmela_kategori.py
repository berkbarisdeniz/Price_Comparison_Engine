from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider

class KozmelaSpider(Spider):
    name = "kozmela"
    allowed_domains = ["kozmela.com"]
    start_urls = ["https://www.kozmela.com/"]
    
    def parse(self, response):
        
        main_categories = list(set(response.css('a.d-flex.align-items-center.w-100.px-1.text-center::attr(href)').getall()))
        print(f"Found categories: {main_categories}")
        for link in main_categories:
            yield response.follow(link, self.parse_category_once)
    
    def parse_category_once(self, response):
        # Her ana kategori için sadece 1 çıktı:
        yield {
            'url': response.url,
        }

process = CrawlerProcess(settings={
    "FEEDS": {
        "categories_kozmela.json": {"format": "json"},
    },
    "LOG_LEVEL": "ERROR",
})

process.crawl(KozmelaSpider)
process.start()