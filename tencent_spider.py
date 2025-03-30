import time
import scrapy
from scrapy.http import HtmlResponse
from DrissionPage import ChromiumPage
from news_crawl.items import NewsCrawlItem


class TencentSpider(scrapy.Spider):
    name = "tencent"
    start_urls = ["https://news.qq.com/"]
    max_articles = 150  # 设置最大爬取文章数量
    article_count = 0  # 初始化文章计数器

    def __init__(self, *args, **kwargs):
        super(TencentSpider, self).__init__(*args, **kwargs)
        # 初始化 DrissionPage
        self.page = ChromiumPage()

    def parse(self, response):
        # 使用 DrissionPage 渲染页面
        self.page.get(response.url)

        # 模拟滚动加载更多文章
        self.scroll_to_load_more(10)  # 滚动 10 次

        # 等待页面加载完成（可以根据需要调整等待时间）
        time.sleep(5)  # 等待 5 秒

        # 获取渲染后的页面内容
        html = self.page.html
        response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        # 定位文章列表区域
        articles = response.css('div.channel-feed-item')

        for article in articles:
            item = NewsCrawlItem()

            # 提取文章标题
            item['title'] = article.css('a.article-title span::text').get()

            # 提取文章 URL
            item['url'] = article.css('a.article-title::attr(href)').get()

            # 提取发布时间（列表页中的“小时前”）
            item['publish_time_relative'] = article.css('div.article-media span.time::text').get()

            # 如果标题或 URL 为空，跳过该文章
            if not item['title'] or not item['url']:
                continue

            # 请求文章详情页
            yield scrapy.Request(
                url=response.urljoin(item['url']),
                callback=self.parse_article,
                meta={'item': item}
            )

            # 增加文章计数器
            self.article_count += 1

            # 打印当前文章计数器
            print(f"Scraped article {self.article_count}: {item['title']}")

            # 如果达到最大文章数量，关闭爬虫
            if self.article_count >= self.max_articles:
                self.crawler.engine.close_spider(reason='Max articles reached')
                return

    def parse_article(self, response):
        item = response.meta['item']

        # 提取具体的发布时间（详情页中的 YYYY-MM-DD HH:MM 格式）
        item['publish_time'] = response.css('p.media-meta span::text').get()

        # 提取文章内容
        item['content'] = ''.join(response.css('div.rich_media_content p::text').getall()).strip()



        # 如果内容为空，跳过该文章
        if not item['content']:
            return

        yield item

    def scroll_to_load_more(self, scroll_times):
        """
        模拟滚动页面，加载更多文章
        :param scroll_times: 滚动次数
        """
        print(f"Scrolling to load more articles ({scroll_times} times)...")
        for _ in range(scroll_times):
            # 滚动到页面底部
            self.page.scroll.to_bottom()
            # 等待页面加载更多内容
            time.sleep(2)  # 等待 2 秒
        print(f"Finished scrolling {scroll_times} times")

    def closed(self, reason):
        # 关闭 DrissionPage
        self.page.close()