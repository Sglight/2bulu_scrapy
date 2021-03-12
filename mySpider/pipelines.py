# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MyspiderPipeline:
    def process_item(self, item, spider):
        # print(item)
        if item["itemType"] == "trackId":
            file = open("json.txt", "a")
            url = "http://www.2bulu.com/track/get_track_positions_list4.htm?trackId=" + item["trackId"]
        elif item["itemType"] == "gpxDownloadUrl":
            file = open("gpx.txt", "a")
            url = item["gpxDownloadUrl"]
        file.write(url + "\n")
        file.close()
        return item
