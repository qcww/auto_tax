#coding=utf-8

import requests
import json
import re
import random
import os
import configparser
import time
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
        self.config_file = 'config.ini'
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
        
        screenImg = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',5))+'.png'
        img_url = element.get_attribute('src')

        #保存图片数据  
        data = urllib.request.urlopen(img_url).read()
        f = open(screenImg, 'wb')
        f.write(data)
        f.close()
        return screenImg

        # # 浏览器页面截屏
        # driver.get_screenshot_as_file(screenImg)
        # # 定位验证码位置及大小
        # location = element.location
        # print('location',location)
        # size = element.size

        # # 获取验证码定位
        # left = location['x']
        # top = location['y']
        # right = location['x'] + size['width']
        # bottom = location['y'] + size['height']
        # # 从文件读取截图，截取验证码位置再次保存
        # print('ltrb')
        # img = Image.open(screenImg).crop((left, top, right, bottom))
        # #下面对图片做了一些处理
        # img = img.convert('RGBA')  # 转换模式：L | RGB
        # img = img.convert('L')  # 转换模式：L | RGB
        # img = ImageEnhance.Contrast(img)  # 增强对比度
        # img = img.enhance(2.0)  # 增加饱和度
        # img.save(screenImg)
        # return screenImg

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
    def post_data(self,_cookie,url,data):
        header = {
            'Origin': 'https://etax.anhui.chinatax.gov.cn',
            # 'Host': 'etax.anhui.chinatax.gov.cn', 
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Cookie':_cookie
        }
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

    # 读取 配置>option>key 的值
    def get_config(self,section,key):
        return re.sub(r'#53','%',self.config.get(section,key))

    # 写入配置
    def set_config(self,section,key,value):
        set_val = str(value)
        self.config.set(section,key,re.sub(r'%','#53',set_val.strip('|')))
        self.config.write(open(self.config_file,'w',encoding='utf-8'))