
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import os
import time
import json


class spider(object):
    def __init__(self,type,page):
        self.type=type
        self.page=page
        self.spiderUrl='https://www.zhipin.com/c101010100/?query=%s&city=100010000&page=%s'

    def startBrower(self):
        service = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        # 告诉浏览器不是测试环境
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        brower = webdriver.Chrome(service=service, options=options)
        return brower

    def main(self,page):
        # if(self.page>page):
        #     return
        brower = self.startBrower()
        print("爬取ing:"+self.spiderUrl % (self.type,self.page))
        #加载页面
        brower.get(self.spiderUrl % (self.type,self.page))
        time.sleep(8)
        # 获取所有得li value中孙以下的标签用//表示  然后是标签 中括号 属性
        job_list = brower.find_elements(by=By.XPATH, value='//ul[@class="job-list-box"]/li')
        for index,job in enumerate(job_list):
            print("正在爬取得个数:%d"% index)
            #按照写入的顺序进行爬取，首先是title
            title=job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-title')]/span[@class='job-name']").text
            addresses = job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-title')]/span[@class='job-area-wrapper']/span").text.split('·')
            address=addresses[0]
            #dist
            if len(addresses)!=1:
                dist=addresses[1]
            else:dist=''
            # type
            type=self.type
            #岗位相关
            tar_list= job.find_elements(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/ul[@class='tag-list']/li")
            if len(tar_list) == 2:
                educational=tar_list[1].text
                workExperience=tar_list[0].text
            else:
                educational = tar_list[2].text
                workExperience = tar_list[1].text
            hrName=job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/div[@class='info-public']").text
            hrWork=job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/div[@class='info-public']/em").text
            #workTag  原代码输出的元素没有解码
            workTag = [element.text for element in job.find_elements(by=By.XPATH, value="./div[contains(@class,'job-card-footer')]/ul[@class='tag-list']/li")]

            #默认设置为不是实习
            pratice=0
            #工资 两种工资形式分别处理
            salaries=job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/span[@class='salary']").text
            # 原代码写的是直接 if salaries.find('K') 但是，在测试的时候发现结果是-1时判断为true
            if salaries.find('K')!=-1:
                salaries=salaries.split('·')
                if len(salaries) == 1:
                    salary=list(map(lambda x:int(x)*1000,salaries[0].replace('K','').split('-')))
                    salarymonth='0薪'
                else:
                    salarymonth=salaries[1]
            else:
                salary=list(map(lambda x:int(x),salaries[0].replace('元/天','').split('-')))
                salarymonth='0薪'



    def init(self):
        if not os.path.exists('./temp.csv'):
            with open('./temp.csv', 'a',newline='',encoding='utf-8') as wf:
                writer = csv.writer(wf)
                writer.writerow(["title","address","type","educational","workExperience",
                                 "workTag","salary","salaryMonth""companyTags", "hrWork",
                                 "hrName", "pratice", "companyTitle", "companyAvatar","companyNature",
                                 "companyStatus","companyPeople","detailUrl","companyUrl","dist"])

if __name__ == '__main__':
    spiderObj=spider('python',1)
    spiderObj.init()
    spiderObj.main(10)
