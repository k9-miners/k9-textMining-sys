# -*- coding: utf-8 -*-
import scrapy
from  nutrition_and_you.items import NutritionAndYouItem
import uuid

class Spider1Spider(scrapy.Spider):
    name = 'spider1'
    start_urls = ["https://www.nutrition-and-you.com/sitemap.html"]

    def parse(self, response):
            urls = response.xpath("//div[contains(@class, 'w3-threequarter w3-container')]//@href").extract()
            #urls = urls[2:297]
            urls = urls[2:297]

            for url in urls:
                yield scrapy.Request(url, callback=self.parse_menu_contents)
    
    def parse_menu_contents(self, response):
        item = NutritionAndYouItem()

        item['ID']= str(uuid.uuid4())

        item['title']= response.xpath("//h1//text()").extract()
        
        FirstColumn = SecondColumn = ThirdColumn = []

        if response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[1]/descendant::text()").extract()!=[] :
            FirstColumn = FirstColumn + response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[1]/descendant::text()").extract()
            if response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[2]/descendant::text()").extract()!=[] :
                SecondColumn = SecondColumn + response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[2]/descendant::text()").extract()
                if response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[3]/descendant::text()").extract()!=[] :
                    ThirdColumn = ThirdColumn + response.xpath("//div[contains(@class, 'w3-row w3-padding-16')]//div[contains(@class, 'w3-third w3-container')]//tr/td[3]/descendant::text()").extract()
                else:
                    ThirdColumn = ThirdColumn + []
            else:
                SecondColumn = SecondColumn + []
        else:
            FirstColumn = FirstColumn + []


        #//div[contains(@class, 'w3-row')]//div[contains(@class, 'w3-twothird w3-container')]/p/descendant::text()
        #//li/p
        content=[]
        content = content + response.xpath("//p//descendant::text()").extract()
        item['content'] = content + FirstColumn + SecondColumn + ThirdColumn

        item['url']= response.xpath("//meta[@property='og:url']//@content").extract()

        yield item
