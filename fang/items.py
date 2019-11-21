# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field,Item


class NewHouseItem(Item):
    # 省份
    province = Field()
    # 城市
    city = Field()
    # 小区的名字
    name = Field()
    # 价格
    price = Field()
    # 几局，这个是一个列表
    rooms = Field()
    # 面积
    area = Field()
    # 地址
    addrees = Field()
    # 行政区
    district = Field()
    # 是否在售
    sale = Field()
    # 房天下详细页面的url
    origin_url = Field()


class EsfHouseItem(Item):
    # 省份
    province = Field()
    # 城市
    city = Field()
    # 联系
    contact = Field()
    # 小区的名字
    name = Field()
    # 几室几厅
    rooms = Field()
    # 楼层
    floor = Field()
    # 朝向
    toward = Field()
    # 年代
    year = Field()
    # 地址
    address = Field()
    # 建筑面积
    area = Field()
    # 总价
    price = Field()
    # 单价
    unit = Field()
    # 房源url
    origin_url = Field()