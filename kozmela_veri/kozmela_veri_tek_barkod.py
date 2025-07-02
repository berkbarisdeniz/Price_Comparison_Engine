import json
import time
import re
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy import Request
from scrapy.exceptions import CloseSpider

class AllKozmelaSpider(Spider):
    name = "all_kozmela"
    allowed_domains = ["kozmela.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_barcode = "8690644303432"
        self.found_target = False

        with open("categories_kozmela.json", "r", encoding="utf-8") as f:
            self.category_links = [item["url"] for item in json.load(f)]

    def start_requests(self):
        self.start_time = time.time()
        # Kategorileri sırayla değil, paralel olarak başlatıyoruz
        for url in self.category_links:
            print(f"➡️ Kategori başlatılıyor: {url}")
            yield Request(url, callback=self.parse, meta={"base_url": url, "page": 1})

    def parse(self, response):
        if getattr(self, 'found_target', False):
          return
        base_url = response.meta["base_url"]
        current_page = response.meta["page"]

        products = response.css('div.product-item')
        if not products:
            self.logger.info(f"🚫 Ürün bulunamadı, kategori tamamlandı: {base_url}")
            return  # kategori bitti, diğer kategoriler zaten paralel

        if current_page :
            print(f"🔄 {base_url} - {current_page}. sayfa")

        for product in products:
            product_name = product.css('a.product-title::text').get()
            price = product.css('span.product-price::text').get()
            product_link = product.css('a.product-title::attr(href)').get()
            if product_link:
                product_link = response.urljoin(product_link)
                yield response.follow(product_link, self.parse_product_detail, meta={
                    'product_name': product_name.strip() if product_name else None,
                    'price': price.strip() if price else None,
                    'product_url': product_link
                })

        # Son sayfa numarasını bul
        last_page_link = response.css('a.last::attr(href)').get()
        last_page_num = None
        if last_page_link:
            match = re.search(r'pg=(\d+)', last_page_link)
            if match:
                last_page_num = int(match.group(1))

        # Eğer sayfa numarası varsa ve daha sayfa varsa devam et
        if last_page_num and current_page < last_page_num:
            next_page = current_page + 1
            next_url = f"{base_url}?pg={next_page}"
            yield Request(next_url, callback=self.parse, meta={"base_url": base_url, "page": next_page})
        elif not last_page_num and products:
            # Sayfa numarası yok ama ürün varsa bir sonraki sayfaya geç
            next_page = current_page + 1
            next_url = f"{base_url}?pg={next_page}"
            yield Request(next_url, callback=self.parse, meta={"base_url": base_url, "page": next_page})
        else:
            # Kategori bitti, döngü zaten paralel, burada ekstra işlem yapmaya gerek yok
            pass

    def parse_product_detail(self, response):
        if self.found_target:
            return
        product_name = response.meta['product_name']
        price = response.meta['price']
        product_url = response.meta['product_url']
        barcode = response.css('div.barcode-code span#supplier-barcode-code::text').get()

        if barcode:
            barcode = barcode.strip()
            if barcode == self.target_barcode:
                self.found_target = True
                yield {
                    'product_name': product_name,
                    'price': price,
                    'barcode': barcode,
                    'url': product_url,
                }
                raise CloseSpider(reason=f"Target barcode {self.target_barcode} found")
                
    def close(self, reason):
        end_time = time.time()
        duration = end_time - self.start_time
        print("\n🎉 Scrapy işlemi tamamlandı ve dosya düzgün kapatıldı.")
        print(f"⏱️ Toplam çalışma süresi: {duration:.2f} saniye")
        print(f"Spider kapandı: {reason}")

process = CrawlerProcess(settings={
    "FEEDS": {
        "kozmela_all_products.json": {"format": "json", "encoding": "utf-8"},
    },
    "LOG_LEVEL": "ERROR",
    # Hızlandırma ayarları
    "CONCURRENT_REQUESTS": 16,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 16,
    "CONCURRENT_REQUESTS_PER_IP": 16,
    "DOWNLOAD_DELAY": 0,
    "AUTOTHROTTLE_ENABLED": False,
})

process.crawl(AllKozmelaSpider)
process.start()
