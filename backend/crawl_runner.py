import os
import django
import uuid
import sys



from scrapy_crawler.scrapy_crawler.spiders.trangvang import TrangVangSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler_app.models import CrawlTask, BusinessData


#task_id = int(sys.argv[1])
#url_filter = sys.argv[2]
def create_and_run_task(id, url_filter):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    django.setup()

    #task = CrawlTask.objects.create(url_filter=url_filter, status='pending')
    task = CrawlTask.objects.get(id=id)
    #print(f"Created task #{task.id}")

    try:
        task.status = 'In Progress'
        task.save()

        # Config scrapy settings
        process = CrawlerProcess(get_project_settings())

        # Truyền task id và url filter vào spider
        process.crawl(TrangVangSpider, task_id=task.id, url=url_filter)

        # Chạy đồng bộ, không cần asyncio
        process.start()

        task.refresh_from_db()
        if task.status != 'Failed':
            task.status = 'Done'
            task.save()
            print(f"✅ Task #{task.id} done.")

    except Exception as e:
        print(f"❌ Crawl failed: {e}")
        task.status = 'failed'
        task.save()


