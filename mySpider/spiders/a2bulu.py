import scrapy
import re
import json
import logging
from mySpider.items import MyspiderItem

logger = logging.getLogger(__name__)

class A2buluSpider(scrapy.Spider):
    name = '2bulu'
    allowed_domains = ['2bulu.com']
    start_urls = ['www.2bulu.com/login.htm']

    # 用于登录的账号密码
    username = "YOUR_USER_NAME"
    password = "YOUR_PASSWORD"

    pageNumber = 1 # 搜索开始页数
    endPage = -1 # 限制爬取页数，-1 为无限

    def start_requests(self):
        login_info = dict(
            areaCode = "86",
            username = self.username,
            password = self.password,
            loginCode = "1"
        )

        yield scrapy.FormRequest(
            url = "http://www.2bulu.com/space/user_login.htm",
            formdata = login_info,
            callback = self.search_start,
            dont_filter = True
        )

    def search_start(self, response):
        login_result = self.check_login(response)
        if (login_result == False): return

        yield from self.search_function(response)

    def search_result(self, response):
        href = response.css(".guiji_discription a::attr(href)").extract()
        for item in href:
            pattern = re.compile(r'^(\/track\/t-)(.*)(\.htm)$') # /track/t-XXXXXXXXXXXXXX.htm
            matches = pattern.match(item)
            if matches:
                trackId = matches.group()[9: -4]
                url = "http://www.2bulu.com/space/download_track.htm?trackId={}&type=3".format(trackId)

                item = MyspiderItem()
                item["trackId"] = trackId
                item["itemType"] = "trackId"
                yield item
                
                yield scrapy.Request(
                    url = url,
                    callback = self.track_download_gpx,
                    dont_filter = True
                )
        # 翻页
        next_page = response.xpath("//div[@class='pages']//a/text()")[-1]
        if next_page.extract() == "下一页":
            self.pageNumber += 1

            # 限制页数
            if self.endPage != -1 and self.pageNumber > self.endPage: return

            # 搜索表单
            yield from self.search_function(response)
        else:
            return

    def check_login(self, response):
        result = json.loads(response.text)["message"]
        if result == "SUCCESS":
            return True
        elif result == "NAME_ERROR":
            logger.error("[Login] 用户名错误！")
            return False
        elif result == "PWD_ERROR":
            logger.error("[Login] 密码错误！")
            return False
        else:
            logger.error("[Login] 未知错误！")
            return False

    def search_function(self, response):
        post_data = dict(
            key = "梧桐山",
            pageNumber = str(self.pageNumber),
            sortType = "0",
            trackType = "8", # 步行
            minMileage = "0",
            maxMileage = "30000" # 轨迹长度限制为 0-30km
        )
        yield scrapy.FormRequest(
            url = "http://www.2bulu.com/track/track_search_result.htm",
            formdata = post_data,
            callback = self.search_result,
            dont_filter = True
        )
    
    def track_download_gpx(self, response):
        code = json.loads(response.text)["code"]
        if code == "2":
            url = json.loads(response.text)["url"]
            item = MyspiderItem()
            item["gpxDownloadUrl"] = url
            item["itemType"] = "gpxDownloadUrl"
            yield item
        else:
            logger.error("[GPX] 无法获取 gpx 下载链接。")
