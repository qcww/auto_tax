#coding=utf-8

import requests
import json
import re
import random
import regedit
import os
import configparser
import time
import datetime
import sys
import urllib.request
from time import sleep
from urllib.parse import urlencode  #Python内置的HTTP请求库
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from html.parser import HTMLParser
from PIL import Image, ImageEnhance

#HTML解析
class HTool(HTMLParser):

    a_text = False
    content_array = []
    upload_code_img_url = 'http://toa.hfxscw.com/?r=ocr/parse-code-img' # 上传并解析验证码的地址
     

    def __init__(self):
        self.config_file = "config.ini"
        self.uid,_ = regedit.get_pc_id()
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file,encoding='utf-8')
        self.sb_table_url = self.config['link']['sb_table_url']

    def rt_config(self):
        return self.config    
    
    def handle_starttag(self,tag,attr):  
        if tag == self.starttag:  
            self.a_text = True  
            #print (dict(attr))  
              
    def handle_endtag(self,tag):  
        if tag == self.endtag:  
            self.a_text = False  
              
    def handle_data(self,data):
        if self.a_text:
            data = data.strip()
            self.content_array.append(data)
            
    def table_to_array(self, html):
        tr_array = re.findall(r"<tr.*?>(.*?)</tr>", html, flags=re.DOTALL)
        self.table_array = []
        for index in range(len(tr_array)):
            self.table_array.append([])
            self.content_array = []
            #print('index:' + str(index) + ', value:' + list1[index])
            #print(tr_array[index])
            self.tr_index = index
            self.starttag = 'td'
            self.endtag = 'td'       
            self.feed(tr_array[index])
            self.close()
            self.table_array[index] = self.content_array
        
        return self.table_array

    # 使用截屏方式保存验证码
    def save_ercode_img(self,driver):
        element = driver.find_element_by_xpath("//form[@id='fm3']/div//div/img")

        # # 刷新一下
        # Action = ActionChains(driver)# 实例化一个action对象
        # code_click = Action.click(element)
        # code_click.perform()
        # sleep(2)
        
        save_name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',5))+'.png'
        img_url = element.get_attribute('src')

        #保存图片数据  
        data = urllib.request.urlopen(img_url).read()
        f = open(save_name, 'wb')
        f.write(data)
        f.close()
        self.convert_img(save_name)
        return save_name

    def convert_img(self,save_name):
        img = Image.open(save_name).crop((0, 0, 60, 30))
        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if (pixels[i,j][0] > 100 or pixels[i,j][1] > 100 or pixels[i,j][2] > 100) and pixels[i,j] != (0,0,0):
                    pixels[i,j] = (254, 255, 255)
                else:
                    pixels[i,j] = (0, 0, 0)
        img.save(save_name)

    # 默认按三个月拆分
    def split_time(self,sbrqq,sbrqz,period = 3):
        sbrqq_time = int(time.mktime(time.strptime(sbrqq,"%Y-%m-%d")))
        sbrqz_time = int(time.mktime(time.strptime(sbrqz,"%Y-%m-%d")))
        period_time = period * 30 * 24 * 3600
        end = True
        
        if sbrqq_time + period_time < sbrqz_time:
            # sbrqq_time =  sbrqq_time + period_time
            sbrqz_time = sbrqq_time + period_time
            end = False

        qq_time = time.localtime(sbrqq_time)
        qz_time = time.localtime(sbrqz_time)
        return time.strftime("%Y-%m-%d",qq_time),time.strftime("%Y-%m-%d",qz_time),end



    # 上传图片
    def send_img(self,img_path, img_type='image/png'):
        file_handle = open(img_path, 'rb')

        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'} 
        file = {'image':(img_path, file_handle, 'image/png')}
        r = requests.post(url=self.upload_code_img_url, headers=headers,files=file)

        file_handle.close()

        try:
            os.remove(img_path)
        except(FileNotFoundError):
            print("文件不存在")
        return json.loads(r.text)

	# 获取浏览器cookie resquest post请求获取数据
    def post_data(self,_cookie,url,data,header_add = {}):
        header = {
            'Origin': 'https://etax.anhui.chinatax.gov.cn',
            # 'Host': 'etax.anhui.chinatax.gov.cn', 
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie':_cookie
        }
        header = dict(header,**header_add)
        sleep(1)
        r = requests.post(url, data=data,headers=header)
        return r
        
    def get_data(self, _cookie, url):
        header = {
            'Origin': 'https://etax.anhui.chinatax.gov.cn',
            # 'Host': 'etax.anhui.chinatax.gov.cn', 
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie':_cookie
        }

        r = requests.get(url, headers=header)
        return r


    def formatVar(self,a,key):
        if a.get(key) == None:
            return ""
        return a.get(key)

	# 拼接申报数据详情信息链接
    def open_cell(self,i):
        if i.get('SBUUID') and i.get('SBUUID') != None:
            sbuuid = 'SBUUID'
        else:
            sbuuid = 'JYLSH'

        # if i.BBLX == "2":
        #     g = self.formatVar(i.BDDM)
        #     h = self.getFssrViewUrl(g)
        #     d = "?bddm=" + g + "&sbuuid=" + self.formatVar(sbuuid) + "&pzxh=" + self.formatVar(i.YZPZXH)
        #     return h + d
        
        if i['SBFS_DM'] == "32":
            e = "Y"
        else:
            e = "N"

        if i['SBFS_MC'] == "网络申报":
            f = "Y"
        else:
            f = "N"  

        c = e + f
        b = "bddm=" + self.formatVar(i,'BDDM') + "&ywid=" + self.formatVar(i,sbuuid) + "&ywlx=" + self.formatVar(i,'YWLX') + "&ssqq=" + self.formatVar(i,'SKSSQQ') + "&ssqz=" + self.formatVar(i,'SKSSQZ') + "&sbrq=" + self.formatVar(i,'SBRQ_1') + "&filePath=" + self.formatVar(i,'RECORD_FILEPATH') + "&bbckbz=" + self.formatVar(i,'BBCKBZ') + "&djxh=" + self.formatVar(i,'DJXH') + "&pzxh=" + self.formatVar(i,'YZPZXH') + "&isWssb=" + c + "&zldm=" + self.formatVar(i,'YZPZZL_DM')
        a = self.sb_table_url + b
        return a

    def get_month_range(self,start_day,end_day):
        end_arr = end_day.split('-')
        start_arr = start_day.split('-')
        period_arr = []
        # 时间检验
        if (int(end_arr[0] + end_arr[1])) < int(start_arr[0] + start_arr[1]):
            print('开始时间大于结束时间')
            return []

        year_dec = int(end_arr[0]) - int(start_arr[0]) + 1
        for i in range(year_dec):
            app_year = str(int(end_arr[0]) - i)
            if i == 0:
                month_dec = int(end_arr[1])
                if year_dec == 1:
                    range_period = int(end_arr[1]) - int(start_arr[1]) + 1
                else:    
                    range_period = month_dec
            else:
                month_dec = int(end_arr[1])
                range_period = 12

            for m in range(range_period):
                if i == 0:
                    month = str(int(end_arr[1]) - m)
                    if int(month) == int(start_arr[1])-1 and year_dec == 1:
                        print('这里接技术')
                        break
                else:
                    month =  str(12 - m)
                    if int(month) == int(start_arr[1])-1:
                        print('这里结束')
                        break
                period_arr.append("%s-%02d-01" % (app_year,int(month)))

        return period_arr

    # 读取 配置>option>key 的值
    def get_config(self,section,key):
        return re.sub(r'#53','%',self.config.get(section,key))

    # 写入配置
    def set_config(self,section,key,value):
        set_val = str(value)
        self.config.set(section,key,re.sub(r'%','#53',set_val.strip('|')))
        self.config.write(open(self.config_file,'w',encoding='utf-8'))

    #关闭弹框
    def driver_close_alert(self,driver,limit = 1,ret = []):
        try:
            dig_alert = driver.switch_to.alert
            ret.append(dig_alert.text)
            dig_alert.accept()
        except:
            pass
        limit -= 1
        if limit > 0:
            sleep(0.5)
            return self.driver_close_alert(driver,limit)
        return ret

    # 返回本月最后一天日期
    def last_day_of_month(self):
        now_time = datetime.datetime.now()
        year = int(now_time.year)
        month = int(now_time.month)
        day = int(now_time.day)
        any_day = datetime.date(year, month, day)
        
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        return next_month - datetime.timedelta(days=next_month.day)

    # 返回几个月第一个天和最后一天的日期时间
    def month_get(self,period):
        d = datetime.datetime.now()
        dayscount = datetime.timedelta(days=d.day)
        dayto = d - dayscount
        date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59).strftime("%Y-%m-%d")
        if period > 0:
            date_from = self.get_month_first(period)
        else:
            date_from = date_to    
        return date_from, date_to

    # 返回几个月前第一天
    def get_month_first(self, n):
        d = datetime.datetime.today()
        month = d.month
        year = d.year
        for i in range(n):
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
        return datetime.date(year, month, 1).strftime('%Y-%m-01')