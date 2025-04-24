import scrapy
from crawler_app.models import BusinessData, CrawlTask

class TrangVangSpider(scrapy.Spider):
    name = "trangvang"
    allowed_domains = ["trangvangvietnam.com"]
    #start_urls = ["https://trangvangvietnam.com/categories/164160/phu-tung-xe-may-linh-phu-kien-xe-may.html",]
    
    def __init__(self, url=None, task_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.task_id = task_id
        
        
    def parse(self, response):
        for company in response.css("div.shadow.rounded-3.bg-white"):
            name = company.css("h2 a::text").get()
            detail_url = company.css("h2 a::attr(href)").get()
            category = company.css("span.nganh_listing_txt::text").get()

            # Trích xuất sơ bộ các field nếu có
            address = company.css("i.fa-location-dot").xpath("./parent::small//text()").getall()
            address = " ".join([part.strip() for part in address if part.strip()])
            phone = company.css(".listing_dienthoai a::text").get()
            email = company.css(".email_web_section a[href^='mailto']::attr(href)").re_first(r"mailto:(.+)")
            website = company.css(".email_web_section a[href^='http']::attr(href)").get()

            # Gửi thông tin sang hàm chi tiết nếu thiếu field
            yield response.follow(detail_url, callback=self.parse_detail, meta={
                "name": name,
                "category": category,
                "address": address,
                "phone": phone,
                "email": email,
                "website": website,
                "detail_url": response.urljoin(detail_url),
            })

    def parse_detail(self, response):
        # Nếu thông tin bị thiếu ở trang list, ta cố gắng lấy lại ở trang detail
        def get_if_none(key, value_from_detail):
            return response.meta[key] or value_from_detail

        address = response.css("div.pb-2.pt-0.ps-3.pe-3.m-0").xpath(".//text()").getall()
        address = " ".join([part.strip() for part in address if part.strip()])
        
        data = {
            "name": response.meta["name"],
            "category": response.meta["category"],
            "address": get_if_none("address",address),
            "phone": get_if_none("phone", response.css('a[href^="tel:"]::text').get()),
            "email": get_if_none("email", response.css('a[href^="mailto:"]::attr(href)').re_first(r"mailto:(.+)")),
            "website": get_if_none("website", response.css('a[href^="http"]:not([href*="facebook"])::attr(href)').get()),
            #"url": response.meta["detail_url"],
        }

        try:
            task = CrawlTask.objects.get(id=self.task_id)
            BusinessData.objects.create(task=task, **data)
        except Exception as e:
            self.logger.error(f"❌ Failed to save data: {e}")