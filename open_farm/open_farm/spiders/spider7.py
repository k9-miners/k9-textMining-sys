# -*- coding: utf-8 -*-
import scrapy
import re
import uuid
from open_farm.items import OpenFarmItem

class Spider7Spider(scrapy.Spider):
    name = 'spider7'
    
    start_urls = ['http://openfarm.cc/en/en/crop_search/']

    def parse(self, response):
        
        urls=[]
        urls=urls+response.xpath("//a[contains(@class, 'medium-12 large-6 columns bottom-padding')]/@href").extract()

        for url in urls:
            path="https://openfarm.cc"+url
            yield scrapy.Request(path, callback=self.parse_contents)

    def parse_contents(self, response):
        item=OpenFarmItem()

        item['_id']=str(uuid.uuid4())

        item['title']=response.xpath("//h1[contains(@class, 'crop-name text-center')]//text()").extract()
        
        #table=[]
        #table=table+response.xpath("//div[contains(@class, 'row stage')]//text()").extract()
        #content=[]
        #content=content+response.xpath("//tr/td//text()").extract()
        #overview=[]
        #overview=overview+response.xpath("//div[contains(@class, 'columns large-5 margin-top')]//text()").extract()
        
        item['content']=response.xpath("//tr/td//text()").extract()

        Url = str(response)
        Url = re.sub('<200 ','',Url)
        item['url'] = re.sub('>','',Url)
        
        yield item