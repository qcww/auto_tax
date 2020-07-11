# -*- coding: utf-8 -*- 

import requests
import json
import configparser
import sys
import os
import re
import ChToWod
import xml.dom.minidom
import time
import regedit

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from HTool import HTool
from bs4 import BeautifulSoup


#安徽社保网站
class SbExport:

    def __init__(self,taxObj):
        base_dir = os.getcwd()
        sys.path.append(base_dir)
        self.htool = HTool()
        config = self.htool.rt_config()

        self.login_url = config['link']['ah_sb_login_url']
        self.ah_sb_hd_url = config['link']['ah_sb_hd_url']
        self.taxObj = taxObj
        self.driver = self.taxObj.driver

     #登录
    def login(self,sb_account,sb_pwd):
        self.sb_account = sb_account
        self.sb_pwd = sb_pwd
        self.driver.get(self.login_url)
        #跳过引导
        sleep(3)
        # 尝试登录6次
        return self.login_action(3)

    # 重复尝试登录        
    def login_action(self,login_times):
        driver = self.driver
        
        if login_times == 0:
            # self.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'1','msg':'登录失败次数过多'})
            driver.quit()
            return False
        login_times -= 1
        
        # try:
        tax_code_input = driver.find_element_by_id("username")
        pwd_input = driver.find_element_by_id("password")
        verify_code = driver.find_element_by_xpath("//form[@id='form1']//input[@name='verify']")
        tax_code_input.send_keys(self.sb_account)
        pwd_input.send_keys(self.sb_pwd)
        parse_code = self.parse_action()
        verify_code.send_keys(parse_code)
        # print('解析结果',parse_code)
        driver.execute_script('login()')
        sleep(3)
        curr_link = driver.current_url
        # print('当前链接',curr_link)
        # 判断是否有密码错误的提示框出来 
        try:
            if 'companyInfo' not in curr_link:
                err_msg = driver.find_element_by_xpath("//form[@id='form1']/div[@class='wsbsLoginBg']/div/label").text
                print('错误信息',err_msg)
                if '密码不正确' in err_msg or '用户名不存在' in err_msg:
                    print('账号密码错误')
                    driver.quit()
                    return False
                # 如果是计算结果错误,可重试
                if '验证码有误' in err_msg:
                    self.driver.execute_script("window.location.reload()")
                    print("验证码识别结果不正确，请等待")
                    # self.taxObj.remove_task()
                return self.login_action(login_times)
            else:
                return True
        except :
            print('登录解析时发生错误')
            return False

    # 解析验证码，直到获取到一个结果为止        
    def parse_action(self):
        #保存验证码图片到本地 并识别
        htool = HTool()
        local_img = htool.save_ercode_img(self.driver,"//img[@id='image']")
        res = htool.send_img(local_img)

        if res['parse']:
            print('')
            return res['parse']
        else:
            print('解析验证码失败，重新解析')
            sleep(2)
            return self.parse_action()



    # 获取申报数据 
    def get_sb_data(self):
        htool = HTool()
        period = time.strftime("%Y%m",time.localtime())
        # next_month = htool.get_1st_of_next_month()
        # next_period = next_month.strftime("%Y%m")

        post_data ={"qsrq00":period,"jzrq00":period,"aae140":"","aae078":"","pageIndex":"0","pageSize":"999"}
        sb_ret = htool.post_data(self.ah_sb_hd_url,post_data,self.driver)
        yj_total = 0
        if sb_ret.status_code == 200:
            sb_json = json.loads(sb_ret.text)
            for it in sb_json['data']:
                # print(it['aae002'],next_period)
                # if it['aae002'] != next_period:
                #     continue
                yj_total += float(it['aae022']) + float(it['aae020'])
        return int(yj_total)