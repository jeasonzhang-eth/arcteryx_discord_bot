import time

from scrapyd_api import ScrapydAPI
from scrapyd_api import RUNNING, FINISHED, PENDING

"""
1. fetch_all - 扫描全站
2. fetch_commodities_inventory - 获取某些商品的库存
3.  - 
4.  - 
5.  - 

需要在redis中记录本次爬取和上次爬取的结果的区别
bot只负责发指令调用爬虫
爬下来的信息全部存在redis中
http://localhost:6800/listjobs.json?project=myproject | python -m json.tool
bot可以通过给 listjobs.json 发命令来查看当前运行着哪些爬虫，这些爬虫的运行状况是怎样的？
需要把不同的爬取功能分割到多个爬虫里面，这样就可以单独运行某个爬虫，执行某段爬取逻辑

"""


class ScrapyProxy:
    def __init__(self, project, spider):
        self.scrapyd = ScrapydAPI('http://localhost:6800')
        # 项目名称和爬虫名称
        self.project = project
        self.spider = spider

    def get_spiders(self):
        return self.scrapyd.list_spiders(self.project)

    def get_jobs(self):
        return self.scrapyd.list_jobs(self.project)

    def check_job(self, job_id):
        while True:
            state = self.scrapyd.job_status(self.project, job_id)
            print("还没有完成，继续等待")
            if state == FINISHED:
                print("已完成")
                return True
            time.sleep(2)

    def run_spider(self, settings):
        # 调度爬虫
        job_id = self.scrapyd.schedule(self.project, self.spider, settings=settings)
        print(f"任务 ID: {job_id}")
        return self.check_job(job_id)

    def update_commodities_links(self, settings: dict):
        if self.spider != "update_commodities_links":
            return None
        return self.run_spider(settings)

    def crawl_skus(self, settings):
        if self.spider != "crawl_skus":
            return None
        return self.run_spider(settings)


# sku_list = []
# 输入变量类型

# data = {
#   "project": "LuxuryInfoSpider",
#   "spider": "arcteryx",
#   "settings": {
#     "TYPE": "fetch_all",
#     "SKUS": sku_list
#   }
# }
# response = requests.post(url, json=data)

# data = {
#     "project": "myspider",
#     "spider": "myspider",
#     "setting": "MY_PARAM=new_value",
# }
#
# response = requests.post(url, data=data)
#
# if response.status_code == 200:
#     print("任务调度成功！")
# else:
#     print(f"任务调度失败！状态码: {response.status_code}")
