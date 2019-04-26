# -*- coding: utf-8 -*-
import scrapy
from foodnutritiontable.items import FoodnutritiontableItem
import uuid
import re

class Spider4Spider(scrapy.Spider):
    name = 'spider4'
    start_urls = ["http://www.foodnutritiontable.com/nutritions/minerals/"]

    def parse(self, response):
        alpha=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

        #range(0,26)
        for i in range (0,26):
            if (i==0):
                url = "http://www.foodnutritiontable.com/nutritions/minerals/"
                yield scrapy.Request(url, callback=self.parse_dir_contents)
            else:
                url = "http://www.foodnutritiontable.com/nutritions/minerals/" + alpha[i] + "/"
                yield scrapy.Request(url, callback=self.parse_dir_contents)
    
    def parse_dir_contents(self, response):
        item=FoodnutritiontableItem()

        item['ID']=str(uuid.uuid4())

        title = re.sub('<200 http://www.foodnutritiontable.com/nutritions/minerals/','',str(response))
        title = re.sub('/','',title)
        title = re.sub('>','',title)
        if (title==''):
            item['title']="Minirals of foods A"
        else:
            item['title']="Minirals of foods "+ title

        table=[]
        j=0
        while True:
            try:
                table = table + response.xpath("//div[@id='cphMain_ltvNutrition_pnlRowContainer_"+str(j)+"']/descendant::text()").extract()
                j=j+1
                if response.xpath("//div[@id='cphMain_ltvNutrition_pnlRowContainer_"+str(j)+"']/descendant::text()").extract()==[]:
                    break
            except ValueError:
                break
        
        table=[el.replace('\r','') for el in table]
        table=[el.replace('\t','') for el in table]
        table=[el.replace('\n','') for el in table]
        table=[el.replace(' ','') for el in table]
        
        while True:
            try:
                table.remove('')
            except ValueError:
                break

        #column
        for k in range (0,j):
            #row
            for l in range (0,10):
                if l==0:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinNa_"+str(k)+"']/descendant::text()").extract()
                elif l==1:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinK_"+str(k)+"']/descendant::text()").extract()
                elif l==2:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinCa_"+str(k)+"']/descendant::text()").extract()
                elif l==3:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinP_"+str(k)+"']/descendant::text()").extract()
                elif l==4:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinFe_"+str(k)+"']/descendant::text()").extract()
                elif l==5:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinMg_"+str(k)+"']/descendant::text()").extract()
                elif l==6:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinCu_"+str(k)+"']/descendant::text()").extract()
                elif l==7:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMinZn_"+str(k)+"']/descendant::text()").extract()
                elif l==8:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblFeeling_"+str(k)+"']/descendant::text()").extract()
                elif l==9:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblHealty_"+str(k)+"']/descendant::text()").extract()
                element=[el.replace('\r','') for el in element]
                element=[el.replace('\t','') for el in element]
                element=[el.replace('\n','') for el in element]
                element=[el.replace(' ','') for el in element]
                while True:
                    try:
                        element.remove('')
                    except ValueError:
                        break
                if element==[]:
                    table.insert(((k*11)+(l+1)),'--')

        item['content']=[]
        for m in range (0,j):
            item['content']=item['content']+[(table[m*11],'Sodium= '+table[m*11+1]+'(mg)','Potassium= '+table[m*11+2]+'(mg)','Calcium= '+table[m*11+3]+'(mg)','Phosphor= '+table[m*11+4]+'(mg)','Iron= '+table[m*11+5]+'(mg)','Magnesium= '+table[m*11+6]+'(mg)','Copper= '+table[m*11+7]+'(mg)','Zinc= '+table[m*11+8]+'(mg)','Emotional= '+table[m*11+9],'Helthy= '+table[m*11+10])]

        Url = str(response)
        Url = re.sub('<200 ','',Url)
        item['url'] = re.sub('>','',Url)
        
        yield item
