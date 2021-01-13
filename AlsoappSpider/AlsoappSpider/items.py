# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AlsoappspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BeautyItem(scrapy.Item):
    """ 这是下载校花网的item文件 """
    
    name = scrapy.Field()
    image_url = scrapy.Field()


class QiushibaikeItem(scrapy.Item):
    """ 这是糗事百科的视频下载item """

    content = scrapy.Field()  # 视频内容
    src = scrapy.Field()    # 视频下载url
