# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsCrawlItem(scrapy.Item):
    # 定义爬取的字段
    title = scrapy.Field()  # 文章标题
    content = scrapy.Field()  # 文章内容
    publish_time = scrapy.Field()  # 发布时间
    url = scrapy.Field()  # 文章链接
    publish_time_relative = scrapy.Field()  # 相对发布时间
