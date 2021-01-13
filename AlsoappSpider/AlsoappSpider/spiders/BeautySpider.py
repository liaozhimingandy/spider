import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from AlsoappSpider.items import BeautyItem


class BeautyspiderSpider(CrawlSpider):
    """ 校花网美女图片抓取通用爬虫 """

    name = 'BeautySpider'
    allowed_domains = ['521609.com']
    start_urls = ['http://www.521609.com/daxuemeinv/']
    BASE_URL = "http://www.521609.com/"

    # 自定义请求头
    custom_settings = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/63.0.3239.132 Safari/537.36 QIHU 360SE',
        'ITEM_PIPELINES': {'AlsoappSpider.pipelines.BeautyImageSavePipeline': 200 }
    }

    rules = (
        Rule(LinkExtractor(allow=r'/\d+\.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):

        name = response.xpath("//div[@class='index_img list_center']/div[@class='title']/h2/text()").get()
        image_url = response\
            .xpath("//div[@class='index_img list_center']/div[@class='picbox']/a/img/@src").get()

        # 若有空提取到空的url则跳过,并且打印
        if image_url is None:
            print(f"文件名:{name}的图片地址为空,请手工检查地址:{response.url}")
            return
        image_url = self.BASE_URL + image_url
        item = BeautyItem()
        # item = {'name': name, 'image_url': image_url}
        item['name'] = name
        item['image_url'] = image_url
        # print(f"名字:{name},图片下载地址:{image_url}")
        # 使用spider自带log工具打印日志
        self.logger.info(f"名字:{name},图片下载地址:{image_url}")
        return item


if __name__ == "__main__":
    import os
    import sys
    from scrapy.cmdline import execute

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute('scrapy crawl BeautySpider'.split())
