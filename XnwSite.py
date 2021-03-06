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
from Verify import XnwVerify

# 信诺网
class Xnw:

    def __init__(self,taxObj):
        base_dir = os.getcwd()
        sys.path.append(base_dir)
        self.htool = HTool()
        config = self.htool.rt_config()

        self.login_url = 'https://www.nuocity.com/xnw_user_ssoservice/login?service=https%3A%2F%2Fwww.nuocity.com%2Fxnw%2Fzz%2Flogin.jspx%3FreturnUrl%3Dhttps%253A%252F%252Fwww.nuocity.com%252F%26locale%3Dzh_CN'
        self.ah_sb_hd_url = config['link']['ah_sb_hd_url']
        # 社保账号密码
        self.si_account_ret_url = self.htool.get_link_by_env('si_account_ret_url')
        self.taxObj = taxObj
        self.driver = self.taxObj.driver

    # 设置运行id
    def set_runid(self,runid):
        self.run_id = runid

     #登录
    def login(self,post_data,corpid):
        self.driver.get(self.login_url)
        #跳过引导
        sleep(1)
        # self.driver.execute_script("jumpToFpdk()")
        # sleep(1)
        # self.driver.execute_script("$('.layui-layer-dialog .layui-layer-btn a:eq(0)').click()")
        # 尝试登录
        ret = self.login_action(8)
        post_data['ret'] = ret
        return post_data

    # 重复尝试登录        
    def login_action(self,login_times):
        driver = self.driver
        
        if login_times == 0:
            # self.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'1','msg':'登录失败次数过多'})
            driver.quit()
            return False
        login_times -= 1

        if len(self.taxObj.credit_code) != 11:
            self.driver.execute_script("$('.tab li:eq(1)').click()")
            self.driver.execute_script("$('#username2').val('%s')" % self.taxObj.credit_code)
            self.driver.execute_script("$('#password2').val('%s')" % self.taxObj.pwd)
        else:
            self.driver.execute_script("$('#username0').val('%s')" % self.taxObj.credit_code)
            self.driver.execute_script("$('#password0').val('%s')" % self.taxObj.pwd)
        verify = XnwVerify()
        verify.verify_image(self.driver)
        driver.execute_script("$('#qyboxnr input[name=submit]').click()")

        sleep(2)
        curr_link = driver.current_url
        # print('当前链接',curr_link)
        if curr_link == 'https://www.nuocity.com/':
            return True
        # 判断是否有密码错误的提示框出来
        try:
            pass_err = driver.find_element_by_class_name("layui-layer-dialog")
            if pass_err:
                # print('pass_err',pass_err)
                err_msg = pass_err.find_element_by_xpath("./div[@class='layui-layer-content layui-layer-padding']").text
                print('err_msg',err_msg)
                # print('错误信息',err_msg)
                if '用户名格式不正确' in err_msg or '手机号格式不正确' in err_msg or '用户名不能为空' in err_msg or '密码不能为空' in err_msg or '您输入的用户名或密码不正确' in err_msg or '您输入的手机号或密码不正确' in err_msg:
                    print('账号密码错误')
                    self.htool.post_data(self.taxObj.tax_password_url,{'corpid':self.taxObj.corpid,'xnw_pwd':'0','msg':err_msg})
                    driver.quit()
                    return False
                # 如果是计算结果错误,可重试
                if '图片验证码不正确' in err_msg:
                    print("验证码识别结果不正确，请等待")
                    # self.taxObj.remove_task()
                driver.execute_script("layer.closeAll()")
                return self.login_action(login_times)
            else:
                return True
        except Exception as e:
            print('登录解析时发生错误',e)
        return False

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