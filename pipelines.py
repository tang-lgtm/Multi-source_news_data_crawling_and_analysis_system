# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NewsCrawlPipeline:
    def process_item(self, item, spider):
        return item


import csv
from scrapy.exceptions import DropItem
from hdfs import InsecureClient
import json
from scrapy.exceptions import DropItem



class CsvWriterPipeline:
    seen_urls = set()  # 类变量，用于在多个爬虫运行之间保持URL去重

    def __init__(self):
        self.filename = 'merged_news_data.csv'
        self.file = None
        self.writer = None

    def open_spider(self, spider):
        # 爬虫启动时调用，打开文件并创建CSV writer
        self.file = open(self.filename, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)

        # 如果文件是新创建的，写入标题行
        if self.file.tell() == 0:
            self.writer.writerow(['url', 'title', 'content', 'publish_time'])

    def close_spider(self, spider):
        # 爬虫关闭时调用，关闭文件
        if self.file:
            self.file.close()

    def process_item(self, item, spider):
        # URL去重
        if item['url'] in self.seen_urls:
            raise DropItem(f"Duplicate item found: {item['url']}")
        self.seen_urls.add(item['url'])

        # 清洗数据：确保字段不为空
        if not item['title'] or not item['content'] or not item['publish_time']:
            raise DropItem("Missing content in item")

        # 将数据写入CSV文件
        self.writer.writerow([
            item['url'],
            item['title'],
            item['content'],
            item['publish_time']
        ])
        self.file.flush()  # 确保数据立即写入文件

        return item