# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2020 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : DemoSpider
#   @File Name   : BokeSpider.py
#   @Created Date: 2021-01-09 15:56
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description :
#
# ======================================================================

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from AlsoappSpider.items import QiushibaikeItem


class QiushibaikeSpider(CrawlSpider):
    name = 'qiushibaike'  # 定义此蜘蛛名称
    allowed_domains = ['qiushibaike.com']  # 包含允许此蜘蛛爬网的域
    start_urls = ['https://www.qiushibaike.com/']
    COUNT_DOWNLOAD = 0
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        # 自定义管道
        'ITEM_PIPELINES': {
            'AlsoappSpider.pipelines.QiushibaikeFilePipeline': 201
        }
    }
    BASE_URL = 'https://www.qiushibaike.com'
    # 连接提取器：会去起始url响应回来的页面中提取指定的url
    # 详情页
    link = LinkExtractor(allow=r'/article/')
    # rules元组中存放的是不同的规则解析器（封装好了某种解析规则)
    # 首页,有下一页
    link2 = LinkExtractor(allow=r'/video/')
    rules = (
        # 提取匹配 'category.php' 的链接 （不匹配 'subsection.php'）
        # 没有设置callback，则默认follow=True，继续抓取当前页面符合该条规则的所有链接,如果有下一页的情况,则需要自己进一步处理
        # Rule(LinkExtractor(allow=('',), deny=('',))),
        # 提取匹配 'item.php' 的链接，用parse_item方法做解析,如解析的页面有继续跟进的页面可以设置follow,或者在解析的页面进行设置也可;
        Rule(LinkExtractor(allow=('/video/',)), callback='parse_item_page', follow=True),
        # Rule(link2, callback="parse_item_page"),
        # Rule(link, callback='parse_item'),

    )

    @staticmethod
    def close(spider, reason):
        print(f"爬虫:{QiushibaikeSpider.name}任务结束,共下载文件:{QiushibaikeSpider.COUNT_DOWNLOAD}个")
        return super().close(spider, reason)

    def parse_item_page(self, response):
        # 1.先解析开始爬取的页数据
        content_list = response.xpath("//div[@class='article block untagged mb15 typs_hot']")
        for content_tmp in content_list:
            src = content_tmp.xpath(f'//div[{content_list.index(content_tmp)+1}]/video/source/@src').get()
            content = content_tmp.xpath(f'//div[{content_list.index(content_tmp)+1}]/a/div[@class="content"]'
                                        f'/span/text()').get().replace('\n', '')

            src = "https:" + src

            yield QiushibaikeItem(content=content, src=src)

            self.COUNT_DOWNLOAD += 1
            #  item

        # 开始分页查询
        # 首先我们要找到下一页 地址
        next_page = response.xpath("//ul[@class='pagination']/li[last()]/a/@href").get()
        current_page = response.xpath("//ul[@class='pagination']/li/span[@class='current']/text()").get()\
            .replace('\n', '')

        if current_page:
            print(f"已经解析完成第{current_page}页数据!")

        # 因为页面到最后一页之后下一页不存在，所以到这里就要停止
        if next_page is None:
            return
        else:
            print(self.BASE_URL + next_page)
            # 把请求yield出去交给框架处理，注意我这里加了meta参数，是防止重定向的，不然我这里直接请求会重定向别的错误地址
            yield scrapy.Request(self.BASE_URL + next_page, meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302, 301]
            }, callback=self.parse_item_page, headers=self.custom_settings)

    def parse_item(self, response):
        # self.logger.info('Hi, this is an item page! %s', response.url)

        # item = scrapy.Item()
        # loader = ItemLoader(item=QiushibaikeItem(), selector=response)
        print(f'请求地址:{response.request.url}')
        print("正在解析...")
        div_list = response.xpath('//div[@class="article block untagged noline"]')
        for div in div_list:
            # item = QiushibaikeItem()

            content = div.xpath('//div[@id="single-next-link"]/div/text()').get()
            src = div.xpath('//video[@id="article-video"]/source/@src').get()
            # 链接加上https:
            src = "https:" + src

            if src is None:
                # src = div.xpath(
                #     '//div[@id="single-next-link"]/div[@class="content"]/text()').get()  # 遇到有&nbsp;和<br>后，文本内容没有取全
                src = div.xpath(
                    'normalize-space(//div[@id="single-next-link"]/div[@class="content"])').get()  # normalize-space（）遇到有&nbsp;和<br>后，文本内容正常取

            item = QiushibaikeItem(content=content, src=src)

            yield item
            break
        # item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        # item['name'] = response.xpath('//td[@id="item_name"]/text()').get()
        # item['description'] = response.xpath('//td[@id="item_description"]/text()').get()
        # item['link_text'] = response.meta['link_text']
        # url = response.xpath('//td[@id="additional_data"]/@href').get()
        # 如果需要存储的数据在另外一个页面,则进一步跟踪,并且传入本次匹配的数据
        # return response.follow(url, self.parse_additional_page, cb_kwargs=dict(item=item))



    # def parse_additional_page(self, response, item):
    #     item['additional_data'] = response.xpath('//p[@id="additional_data"]/text()').get()
    #     return item


def main():
    import os, sys
    # 导入execute
    from scrapy.cmdline import execute
    sys.path.append(os.path.dirname(os.path.abspath('QiushibaikeSpider.py')))
    execute(['scrapy', 'crawl', 'qiushibaike'])


if __name__ == "__main__":
    main()
