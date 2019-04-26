# -*- coding: utf-8 -*-
import scrapy
from nutritionfoundation.items import NutritionfoundationItem
import uuid
import re

class Spider5Spider(scrapy.Spider):
    name = 'spider5'

    start_urls = ['http://nutritionfoundation.org.nz/nutrition-facts/nutrition-a-z/']

    def parse(self, response):
        urls= response.xpath("//div/div[contains(@class, 'views-field views-field-title')]//a/@href").extract()

        for url in urls:
            url = "https://nutritionfoundation.org.nz"+url
            yield scrapy.Request(url, callback=self.parse_contents)
    
    def parse_contents(self, response):
        item=NutritionfoundationItem()

        item['_id']=str(uuid.uuid4())

        item['title']=response.xpath("//h1/text()").extract()

        content=[]
        content=content+response.xpath("//p//text()").extract()
        content=content+response.xpath("//div[contains(@class, 'field__item even')]/ul/li//text()").extract()
        item['content']=content

        Url = str(response)
        Url = re.sub('<200 ','',Url)
        item['url'] = re.sub('>','',Url)

        yield item