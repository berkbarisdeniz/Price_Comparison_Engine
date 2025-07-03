import json
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy import Request
import re
import time
from urllib.parse import urljoin

class AllMarkaFarmaSpider(Spider):
    name = "all_markafarma"
    allowed_domains = ["markafarma.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("categories_markafarma.json", "r", encoding="utf-8") as f:
            self.category_links = [item["url"] for item in json.load(f)]
        self.category_index = 0

    def start_requests(self):
        if self.category_links:
            url = self.category_links[self.category_index]
            print(f"➡️ Başlangıç kategorisi: {url}")
            yield Request(url, callback=self.parse, meta={"base_url": url, "page": 1})

    def parse(self, response):
        base_url = response.meta["base_url"]
        current_page = response.meta["page"]

        products = response.css('div.product-item')
        if not products:
            self.logger.info(f"🚫 Ürün bulunamadı, kategori tamamlandı: {base_url}")
            yield from self.next_category()
            return

        if current_page :
            print(f"🔄 {base_url} - {current_page}. sayfa")

        for product in products:
            product_name = product.css('a.w-100.text-black.fs875.fw-regular.product-title::text').get()
            price = product.css('strong.fw-semibold.product-price::text').get()
            product_link = product.css('a.w-100.text-black.fs875.fw-regular.product-title::attr(href)').get()
            product_link = urljoin(self.allowed_domains[0], product_link)
            
            if product_link:
                product_link = response.urljoin(product_link)
                yield response.follow(product_link, self.parse_product_detail, meta={
                    'product_name': product_name.strip() if product_name else None,
                    'price': price.strip() if price else None,
                    'product_url': product_link
                })

        last_page_link = response.css('a.last::attr(href)').get()
        last_page_num = None
        if last_page_link:
            match = re.search(r'pg=(\d+)', last_page_link)
            if match:
                last_page_num = int(match.group(1))

        if last_page_num:
            if current_page < last_page_num:
                next_page = current_page + 1
                next_url = f"{base_url}?pg={next_page}"
                yield Request(next_url, callback=self.parse, meta={"base_url": base_url, "page": next_page})
            else:
                yield from self.next_category()
        else:
            if products:
                next_page = current_page + 1
                next_url = f"{base_url}?pg={next_page}"
                yield Request(next_url, callback=self.parse, meta={"base_url": base_url, "page": next_page})
            else:
                yield from self.next_category()

    def next_category(self):
        self.category_index += 1
        if self.category_index < len(self.category_links):
            next_url = self.category_links[self.category_index]
            print(f"➡️ Yeni kategoriye geçiliyor: {next_url}")
            yield Request(next_url, callback=self.parse, meta={"base_url": next_url, "page": 1})
        else:
            print("✅ Tüm kategoriler tamamlandı.")

    def parse_product_detail(self, response):
        product_name = response.meta['product_name']
        price = response.meta['price']
        product_url = response.meta['product_url']
        
        barcode = response.css('div.w-100.text-black::text').get()
        barcode = barcode.split(":")[1]
        yield {
            'product_name': product_name,
            'price': price,
            'barcode': barcode.strip() if barcode else None,
            'url': product_url,
        }

process = CrawlerProcess(settings={
    "FEEDS": {
        "markafarma_all_products.json": {"format": "json", "encoding": "utf-8"},
    },
    "LOG_LEVEL": "ERROR",
})

start = time.time()
process.crawl(AllMarkaFarmaSpider)
process.start()

print(f"Execution time: {time.time() - start}")