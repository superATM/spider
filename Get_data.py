import requests
from urllib.parse import urlencode
import pandas as pd
import random
import time
import json
import os
import csv
from lxml import etree
import re


class Lagou_Position(object):

    def __init__(self):
        self.User_Agent = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        ]
        self.headers = {
            "Host":"www.lagou.com",
            "Referer": "https://www.lagou.com/jobs/list_%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8/p-city_2?px=default",
            "User_Agent": random.choice(self.User_Agent),
            "X-Requested-With": "XMLHttpRequest"
        }
        self.headers1 = {
            "Host": "www.lagou.com",
            "Referer": "https://www.lagou.com/jobs/list_%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8/p-city_2?px=default",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(self.User_Agent)
        }
        self.First_url = "https://www.lagou.com/jobs/list_%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8/p-city_2?px=default"
        #搜索网络安全
        self.Target_url = "https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false"
        #网络安全页下ajax页面



    #请求原始链接获得cookie
    def Get_First_Url(self):
        rs = requests.session()
        rs.get(self.First_url, headers = self.headers, timeout=3)
        cookies = rs.cookies
        print(cookies)
        return cookies



    #构造请求Ajax的数据包
    def Post_Target_Url(self):
        cookie = self.Get_First_Url()
        return_cookie = requests.utils.dict_from_cookiejar(cookie)
        cookie.update(return_cookie)
        pn = 1
        for pn in range(30):
            params = {
                "first":"false",
                "pn":pn,
                "kd":"网络安全"
            }
            pn += 1
            response = requests.post(self.Target_url,data=params, cookies = cookie, headers = self.headers, timeout=3)
            print(response.text)
            self.Analysis(response)
            time.sleep(60)

    #解析Ajax返回请求内职位信息
    def Analysis(self,response):
        items = []
        data = json.loads(response.text)["content"]["positionResult"]["result"]
        if len(data):
            for i in range(len(data)):
                positionID = data[i]["positionId"]
                positionName = data[i]["positionName"]
                education = data[i]['education']
                companyShortName = data[i]["companyShortName"]
                workYear = data[i]["workYear"]
                salary = data[i]["salary"] + "*" + data[i]["salaryMonth"]
        self.Save_ajax_data(items)
        time.sleep(1.3)

    # 保存在ajax里收集到的职位和条目信息
    def Save_ajax_data(self, items):
        file_size = os.path.getsize(r'C:\Users\Administrator\PycharmProjects\pythonlearn1\Strain\Lagou_Spider\analyst.csv')
        if file_size == 0:
            name = ["ID","职位名称","学历要求","公司名称","工作年限","薪水待遇"]
            file_test = pd.DataFrame(columns=name, data=items)
            file_test.to_csv(r"analyst.csv", encoding="gbk", index=False)
        else:
            with open(r"analyst.csv", "a+", newline="") as file_test:
                writer = csv.writer(file_test)
                writer.writerows(items)

    #请求职位详情页
    def Get_Url(self):
        urls = []
        with open("analyst.csv","r",newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != "ID":
                    url = "https://www.lagou.com/jobs/{}.html".format(row[0])
                    urls.append(url)
        return  urls

    #对职位详情页的内容进行解析
    def Get_Detail(self):
        urls = self.Get_Url()
        length = len(urls)
        for url in urls:
            description = ""
            print(url)
            rs = requests.get(url, headers = self.headers1)
            rs.encoding = "utf-8"
            time.sleep(5)
            content = etree.HTML(rs.text)
            detail = content.xpath('//*[@id="job_detail"]/dd[2]/div/p/text()')
            print(detail)

            for i in range(1, len(detail)):

                if '要求' in detail[i - 1]:
                    for j in range(i, len(detail)):
                        detail[j] = detail[j].replace('\xa0', '')
                        detail[j] = re.sub('[、;；.0-9。]', '', detail[j])
                        description = description + detail[j] + '/'
                    print(description)
            self.Save_Position_Detail(description)
            length -= 1
            time.sleep(3)
    #保存职位详情页的信息
    def Save_Position_Detail(self,description):
        with open("description.txt", "a+", encoding="utf-8") as file:
            file.write(description)

spider = Lagou_Position()
spider.Post_Target_Url()
spider.Get_Detail()
