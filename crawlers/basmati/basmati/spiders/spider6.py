# -*- coding: utf-8 -*-
import scrapy
import uuid
from basmati.items import BasmatiItem
import re

class Spider6Spider(scrapy.Spider):
    name = 'spider6'
    
    start_urls = ['http://basmati.com/tags/gardening/','https://basmati.com/tags/farming/','https://basmati.com/tags/superfoods/','https://basmati.com/tags/food-medicine/']

    def parse(self, response):

        hrefs = response.xpath("//div[@id='main-content']//a/@href").extract()
        n = len(hrefs)
        #hrefs[0:n-1]
        hrefs = hrefs[0:n-1]
        for href in hrefs:
            url = "http://basmati.com" + href
            yield scrapy.Request(url, callback=self.parse_contents)

    def parse_contents(self, response):
        if (response.xpath("//div[contains(@class, 'field field-name-body field-type-text-with-summary field-label-hidden')]/div[contains(@class, 'field-items')]/div[contains(@class, 'field-item even')]//text()").extract()==[]):
            pass
        else:
            item= BasmatiItem()

            item['_id']= str(uuid.uuid4())

            item['title']=response.xpath("//h1[contains(@class, 'page-header')]//text()").extract()

            item['content']=response.xpath("//div[contains(@class, 'field field-name-body field-type-text-with-summary field-label-hidden')]/div[contains(@class, 'field-items')]/div[contains(@class, 'field-item even')]//text()").extract()

            Url = str(response)
            Url = re.sub('<200 ','',Url)
            item['url'] = re.sub('>','',Url)

            yield item
