# -*- coding: utf-8 -*-
import scrapy
from foodnutritiontable.items import FoodnutritiontableItem
import uuid
import re

class Spider2Spider(scrapy.Spider):
    name = 'spider2'
    start_urls = ["http://www.foodnutritiontable.com/nutritions/"]

    def parse(self, response):
        alpha=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

        #range(0,26)
        for i in range (0,26):
            if (i==0):
                url = "http://www.foodnutritiontable.com/nutritions/"
                yield scrapy.Request(url, callback=self.parse_dir_contents)
            else:
                url = "http://www.foodnutritiontable.com/nutritions/" + alpha[i] + "/"
                yield scrapy.Request(url, callback=self.parse_dir_contents)
    
    def parse_dir_contents(self, response):
        item=FoodnutritiontableItem()

        item['_id']=str(uuid.uuid4())

        title = re.sub('<200 http://www.foodnutritiontable.com/nutritions/','',str(response))
        title = re.sub('/>','',title)
        title = re.sub('>','',title)
        if (title==''):
            item['title']="Nutritional value of foods A"
        else:
            item['title']="Nutritional value of foods "+ title


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
            for l in range (0,14):
                if l==0:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblKcal_"+str(k)+"']/descendant::text()").extract()
                elif l==1:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblKjoule_"+str(k)+"']/descendant::text()").extract()
                elif l==2:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblWater_"+str(k)+"']/descendant::text()").extract()
                elif l==3:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblEiwit_"+str(k)+"']/descendant::text()").extract()
                elif l==4:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblKoolh_"+str(k)+"']/descendant::text()").extract()
                elif l==5:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblSuikers_"+str(k)+"']/descendant::text()").extract()
                elif l==6:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblVet_"+str(k)+"']/descendant::text()").extract()
                elif l==7:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblVerz_"+str(k)+"']/descendant::text()").extract()
                elif l==8:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblEov_"+str(k)+"']/descendant::text()").extract()
                elif l==9:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblMov_"+str(k)+"']/descendant::text()").extract()
                elif l==10:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblChol_"+str(k)+"']/descendant::text()").extract()
                elif l==11:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblVoedv_"+str(k)+"']/descendant::text()").extract()
                elif l==12:
                    element=response.xpath("//span[@id='cphMain_ltvNutrition_lblFeeling_"+str(k)+"']/descendant::text()").extract()
                elif l==13:
                    element=response.xpath("//div[@id='cphMain_ltvNutrition_pnlHealty_"+str(k)+"']/descendant::text()").extract()
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
                    table.insert(((k*15)+(l+1)),'--')

        item['content']=[]
        for m in range (0,j):
            item['content']=item['content']+[(table[m*15],'Energy= '+table[m*15+1]+'(kcal)','Energy= '+table[m*15+2]+'(kJ)','Water= '+table[m*15+3]+'(g)','Protein= '+table[m*15+4]+'(g)','Carbohy= '+table[m*15+5]+'(g)','Sugars= '+table[m*15+6]+'(g)','Fat= '+table[m*15+7]+'(g)','Saturated= '+table[m*15+8]+'(g)','Monoun= '+table[m*15+9]+'(g)','Polyun= '+table[m*15+10]+'(g)','Cholest= '+table[m*15+11]+'(mg)','Fibers= '+table[m*15+12]+'(g)','Emotional= '+table[m*15+13],'Helthy= '+table[m*15+14])]

        Url = str(response)
        Url = re.sub('<200 ','',Url)
        item['url'] = re.sub('>','',Url)
        
        yield item
