import time
import scrapy
from scrapy.http import HtmlResponse
from DrissionPage import ChromiumPage
from news_crawl.items import NewsCrawlItem


class ThePaperSpider(scrapy.Spider):
    name = "thepaper"
    start_urls = ["https://www.thepaper.cn/"]
    max_articles = 600  # 设置最大爬取文章数量
    article_count = 0  # 初始化文章计数器

    def __init__(self, *args, **kwargs):
        super(ThePaperSpider, self).__init__(*args, **kwargs)
        # 初始化 DrissionPage
        self.page = ChromiumPage()

    def parse(self, response):
        # 使用 DrissionPage 渲染页面
        self.page.get(response.url)

        # 点击"时间排序"按钮
        try:
            sort_button = self.page.ele('css selector:.index_changeversion__Mk_bU p:contains(时间排序)')
            if sort_button:
                if 'index_active__v2TqX' not in sort_button.attr('class'):
                    sort_button.click()
                    print("Clicked '时间排序' button")
                    time.sleep(3)  # 等待页面重新加载
                else:
                    print("'时间排序' is already active")
            else:
                print("'时间排序' button not found")
        except Exception as e:
            print(f"Error interacting with '时间排序' button: {e}")

        # 模拟滚动加载更多文章
        self.scroll_to_load_more(20)  # 滚动 10 次

        # 等待页面加载完成（可以根据需要调整等待时间）
        time.sleep(5)  # 等待 5 秒

        # 获取渲染后的页面内容
        html = self.page.html
        response = HtmlResponse(url=response.url, body=html, encoding='utf-8')

        # 定位文章列表区域
        articles = response.css('div.small_toplink__GmZhY')

        for article in articles:
            item = NewsCrawlItem()

            # 提取文章标题
            item['title'] = article.css('h2::text').get()

            # 提取文章 URL
            item['url'] = article.css('a::attr(href)').get()
            if item['url']:
                item['url'] = response.urljoin(item['url'])



            # 如果标题或 URL 为空，跳过该文章
            if not item['title'] or not item['url']:
                continue

            # 请求文章详情页
            yield scrapy.Request(
                url=item['url'],
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

        # 提取发布时间
        item['publish_time'] = response.css('div.ant-space-item span::text').get()

        # 提取文章内容
        content_elements = response.css('div.index_cententWrap__Jv8jK p::text').getall()
        item['content'] = ' '.join([element.strip() for element in content_elements if element.strip()])


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