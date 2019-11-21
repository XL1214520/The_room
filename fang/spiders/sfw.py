# -*- coding: utf-8 -*-
import scrapy,re
from fang.items import NewHouseItem,EsfHouseItem


class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    # 分析全国各地的新房url和二手房的url
    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath('.//td[not(@style)]')
            province_td = tds[0]
            province_text = province_td.xpath('.//text()').get()
            province_text = re.sub(r'\s','',province_text)
            if province_text:
                province = province_text
            if province == '其它':
                continue
            city_td = tds[1]
            city_links = city_td.xpath('.//a')
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                # 构造新房url链接
                url_module = city_url.split(".")
                scheme = url_module[0]
                domain = url_module[1]
                if 'bj.' in domain:
                    newhouse_url = "https://newhouse.fang.com/house/s/"
                    esf_url = "https://esf.fang.com/"
                else:
                    newhouse_url = scheme+".newhouse."+domain+".com/house/s/"
                    # 构造二手房的url链接
                    esf_url = scheme + '.esf.'+domain+".com/"
                yield scrapy.Request(url=newhouse_url,callback=self.parse_newhouse,meta={'info':(province,city)})

                yield scrapy.Request(url=esf_url,callback=self.parse_esf,meta={'info':(province,city)})
                break
            break
    # 解析新房
    def parse_newhouse(self,response):

        province,city = response.meta.get('info')
        # 判断是否class类 包含nl_con
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            NewItem = NewHouseItem()
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").extract()
            # 将空白字符 转换成空字符   小区的名字
            name = list(map(lambda x:re.sub(r'\s','',x),name))
            house_type_list = li.xpath(".//div[contains(@class,'house_type ')]//a/text()").extract()
            # 调用过滤函数filter  以“居”结尾的  几局
            rooms = list(filter(lambda x:x.endswith("居"),house_type_list))
            # 平方
            area = ''.join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub(r"\s|/|－",'',area)

            # 地址
            addrees = li.xpath(".//div[@class='address']/a/@title").extract_first()

            # 区域
            district_text = li.xpath(".//div[@class='address']/a/span/text()").extract()
            district = list(map(lambda x:re.sub(r'\s','',x),district_text))

            # 价格 将列表转换为字符串
            price = ''.join(li.xpath(".//div[@class='nhouse_price']//text()").extract())
            price = re.sub(r'\s|广告','',price)
            # 是否在售
            sale = li.xpath(".//div[contains(@class,fangyuan)]/span/text()").extract_first()
            # 房源链接
            origin_url = str(li.xpath(".//div[@class='nlcd_name']/a/@href").extract_first())
            NewItem["province"] = province
            NewItem["city"] = city
            NewItem["name"] = name
            NewItem["price"] = price
            NewItem["rooms"] = rooms
            NewItem["area"] = area
            NewItem["addrees"] = addrees
            NewItem["district"] = district
            NewItem["sale"] = sale
            NewItem["origin_url"] = origin_url
            NewItem["province"] = province
            NewItem['city'] = city
            yield NewItem
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").extract_first()
        yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_newhouse,meta={"info":(province,city)})


    # 解析二手房
    def parse_esf(self,response):
        province,city = response.meta.get('info')
        dls = response.xpath("//div[contains(@class,'shop_list')]/dl")
        for dl in dls:
            item = EsfHouseItem(province=province,city=city)
            item['name'] = dl.xpath(".//p[@class='add_shop']/a/@title").extract_first()
            item['address'] = dl.xpath(".//p[@class='add_shop']//span/text()").extract_first()
            infos = dl.xpath(".//p[@class='tel_shop']//text()").extract()
            infos = list(map(lambda x:re.sub(r"\s",'',x),infos))
            for info in infos:
                if "厅" in info:
                    item["rooms"] = info
                elif "层" in info:
                    item['floor'] = info
                elif "向" in info:
                    item['toward'] = info
                elif '㎡' in info:
                    item["area"] = info
                elif '建' in info:
                    item['year'] = info
                else:
                    item['contact'] = info
            # 总价
            item['price'] = ''.join(dl.xpath(".//dd[@class='price_right']/span[1]//text()").extract())
            # 单价
            item['unit'] = ''.join(dl.xpath(".//dd[@class='price_right']/span[2]//text()").extract())
            item['origin_url'] = dl.xpath(".//h4[@class='clearfix']/a/@href").extract_first()
            yield item
        next_url = response.xpath("//div[@class='page_al']/p[1]/a/@href").extract_first()
        yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_esf,meta={"info":(province,city)})
