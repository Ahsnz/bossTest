from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time
import json


class spider(object):
    def __init__(self, type, page):
        self.type = type
        self.page = page
        self.spiderUrl = 'https://www.zhipin.com/c101010100/?query=%s&city=100010000&page=%s'

    def startBrower(self):
        # service = Service('./chromedriver.exe')
        service=Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        #boss反爬,复用浏览器
        # options.add_experimental_option('debuaggerAddress', 'localhost:9222')
        # 告诉浏览器不是测试环境
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        brower = webdriver.Chrome(service=service, options=options)
        return brower

    def main(self, page):
        # if(self.page>page):
        #     return
        brower = self.startBrower()
        print("爬取ing:" + self.spiderUrl % (self.type, self.page))
        # 加载页面
        brower.get(self.spiderUrl % (self.type, self.page))
        time.sleep(8)
        # 获取所有得li value中孙以下的标签用//表示  然后是标签 中括号 属性
        job_list = brower.find_elements(by=By.XPATH, value='//ul[@class="job-list-box"]/li')
        have_data_flag=True
        for index, job in enumerate(job_list):
           try:
               job_data = []
               print("正在爬取的个数:%d" % index)
               # 按照写入的顺序进行爬取，首先是title
               title = job.find_element(by=By.XPATH,
                                        value=".//a[@class='job-card-left']/div[contains(@class,'job-title')]/span[@class='job-name']").text
               addresses = job.find_element(by=By.XPATH,
                                            value=".//a[@class='job-card-left']/div[contains(@class,'job-title')]/span[@class='job-area-wrapper']/span").text.split(
                   '·')
               address = addresses[0]
               # dist
               if len(addresses) != 1:
                   dist = addresses[1]
               else:
                   dist = ''
               # type
               type = self.type
               # 岗位相关
               tar_list = job.find_elements(by=By.XPATH,
                                            value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/ul[@class='tag-list']/li")
               if len(tar_list) == 2:
                   educational = tar_list[1].text
                   workExperience = tar_list[0].text
               else:
                   educational = tar_list[2].text
                   workExperience = tar_list[1].text
               hrName = job.find_element(by=By.XPATH,
                                         value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/div[@class='info-public']").text
               hrWork = job.find_element(by=By.XPATH,
                                         value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/div[@class='info-public']/em").text
               # workTag  原代码输出的元素没有解码
               workTag = [element.text for element in job.find_elements(by=By.XPATH,
                                                                        value="./div[contains(@class,'job-card-footer')]/ul[@class='tag-list']/li")]

               # 默认设置为不是实习
               pratice = 0
               # 工资 两种工资形式分别处理
               salaries = job.find_element(by=By.XPATH,
                                           value=".//a[@class='job-card-left']/div[contains(@class,'job-info')]/span[@class='salary']").text
               # 原代码写的是直接 if salaries.find('K') 但是，在测试的时候发现结果是-1时判断为true
               if salaries.find('K') != -1:
                   salaries = salaries.split('·')
                   if len(salaries) == 1:
                       salary = list(map(lambda x: int(x) * 1000, salaries[0].replace('K', '').split('-')))
                       salarymonth = '0薪'
                   else:
                       salarymonth = salaries[1]
               else:
                   salary = list(map(lambda x: int(x), salaries[0].replace('元/天', '').split('-')))
                   salarymonth = '0薪'

               companyTitle = job.find_element(by=By.XPATH,
                                               value=".//div[@class='job-card-right']/div[@class='company-info']/h3/a").text
               companyAvatar = job.find_element(by=By.XPATH,
                                                value=".//div[@class='job-card-right']/div[@class='company-logo']/a/img").get_attribute(
                   "src")
               companyInfos = job.find_elements(by=By.XPATH,
                                                value=".//div[@class='job-card-right']/div[@class='company-info']/ul[@class='company-tag-list']/li")
               if len(companyInfos) == 3:
                   companyNature = companyInfos[0].text
                   companyStatus = companyInfos[1].text
                   companyPeoples = companyInfos[2].text
                   if companyPeoples != '10000人以上':
                       companyPeople = list(map(lambda x: int(x), companyInfos[2].text.replace('人', '').split('-')))
                   else:
                       companyPeople = [0, 10000]
               else:
                   companyNature = companyInfos[0].text
                   companyStatus = '未来融资'
                   companyPeoples = companyInfos[1].text
                   if companyPeoples != '10000人以上':
                       companyPeople = list(map(lambda x: int(x), companyInfos[1].text.replace('人', '').split('-')))
                   else:
                       companyPeople = [0, 10000]

               companyTags = job.find_element(by=By.XPATH,
                                              value="./div[contains(@class,'job-card-footer')]/div[@class='info-desc']").text
               if not companyTags:
                   companyTags = '无'
               else:
                   companyTags = json.dumps(companyTags.split(','))
                   companyTags = companyTags.encode().decode('unicode_escape')

               detailUrl = job.find_element(by=By.XPATH, value=".//a[@class='job-card-left']").get_attribute('href')
               companyUrl = job.find_element(by=By.XPATH,
                                             value=".//div[@class='job-card-right']/div[@class='company-info']/h3/a").get_attribute(
                   'href')
               job_data.append(title)
               job_data.append(address)
               job_data.append(type)
               job_data.append(educational)
               job_data.append(workExperience)
               job_data.append(workTag)
               job_data.append(salary)
               job_data.append(salarymonth)
               job_data.append(companyTags)
               job_data.append(hrWork)
               job_data.append(hrName)
               job_data.append(pratice)
               job_data.append(companyTitle)
               job_data.append(companyAvatar)
               job_data.append(companyNature)
               job_data.append(companyStatus)
               job_data.append(companyPeople)
               job_data.append(detailUrl)
               job_data.append(companyUrl)
               job_data.append(dist)
               self.save_to_csv(job_data)
               if len(job_data) == 0:
                   have_data_flag = False
           except:
                pass
        if have_data_flag:
            page=page+1
            self.main(page)

    def save_to_csv(self,rowData):
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as wf:
            writer = csv.writer(wf)
            writer.writerow(rowData)

    def init(self):
        if not os.path.exists('./temp.csv'):
            with open('./temp.csv', 'a', newline='', encoding='utf-8') as wf:
                writer = csv.writer(wf)
                writer.writerow(["title", "address", "type", "educational", "workExperience",
                                 "workTag", "salary", "salaryMonth","companyTags", "hrWork",
                                 "hrName", "pratice", "companyTitle", "companyAvatar", "companyNature",
                                 "companyStatus", "companyPeople", "detailUrl", "companyUrl", "dist"])


if __name__ == '__main__':
    spiderObj = spider('python', 1)
    spiderObj.init()
    spiderObj.main(1)
