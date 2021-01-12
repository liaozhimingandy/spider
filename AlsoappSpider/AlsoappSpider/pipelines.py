# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from os import path

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from AlsoappSpider.items import QiushibaikeItem

class AlsoappspiderPipeline:
    def process_item(self, item, spider):
        return item


# 校花网图片下载管道
class BeautyImageSavePipeline(ImagesPipeline):

    # 自定义请求头
    custom_settings = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    # 使用这个类, 运行的第一个函数是这个
    def get_media_requests(self, item, info):

        yield scrapy.Request(url=item["image_url"], headers=self.custom_settings, meta={'name': item['name'], 'image_url': item["image_url"]})

    # 第三个运行函数,判断有没有保存成功 ,我该写了没有保存成功者保存在本地文件中,以后进行抓取
    def item_completed(self, results, item, info):
        # 是一个元组，第一个元素是布尔值表示是否成功
        if not results[0][0]:
            with open('img_error.txt', 'a', encoding="utf8") as f:
                error = str(item['name'] + '@' + item['image_url'])
                f.write(error)
                f.write('\n')
                raise DropItem('下载失败')
        return item

    # 第二个运行函数
    # 重命名，若不重写这函数，图片名为哈希，就是一串乱七八糟的名字
    def file_path(self, request, response=None, info=None, *, item=None):
        filepath, shotname, extension = get_filePath_file_name_fileExt(file_url=item["image_url"])
        file_name =item['name'] + extension
        return file_name


# 获取文件路径， 文件名， 后缀名
def get_filePath_file_name_fileExt(file_url):
    """
    获取文件路径， 文件名， 后缀名
    :param file_url:
    :return:
    """
    import os
    filepath, tmpfilename = os.path.split(file_url)
    shotname, extension = os.path.splitext(tmpfilename)
    return filepath, shotname, extension


# 图片,视频下载管道
class QiushibaikeFilePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        if isinstance(item, QiushibaikeItem):
            # 请求头
            heads = {
                "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            }
            # 此处需要注意,当时meta写错,则不会下载视频,如当时写成:meta['item']=item
            print(f'正在保存文件:{item["src"]}')
            yield Request(item['src'], headers=heads, meta=item)
        else:
            return super().get_media_requests(item, info)

    def file_path(self, request, response=None, info=None, *, item=None):
        if isinstance(item, QiushibaikeItem):
            # 获取文件名称
            file_name = path.basename(request.meta["src"])
            return file_name

        else:
            return super().file_path(request, response, info, item=item)


if __name__ == "__main__":
    demo_url = "http://www.521609.com//uploads/allimg/130412/1-130412094244.jpg"
    print(get_filePath_file_name_fileExt(file_url=demo_url))