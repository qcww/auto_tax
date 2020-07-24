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
import math
import random

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from HTool import HTool
from bs4 import BeautifulSoup
from SbSite import SbExport

#税务局网站
class TaxSite:

    def __init__(self,taxObj):
        base_dir = os.getcwd()
        sys.path.append(base_dir)
        self.taxObj = taxObj

        config = self.taxObj.config

        self.login_url = config['link']['login_url']
        self.tax_data_url = config['link']['tax_data_url']
        self.tax_send_url = config['link']['tax_send_url']
        self.tax_password_url = config['link']['tax_password_url']
        self.comp_info_url = config['link']['comp_info_url']
        self.tax_info_url = config['link']['tax_info_url']
        self.tax_corp_info_url = config['link']['tax_corp_info_url']
        self.tax_confirm_info_url = config['link']['tax_confirm_info_url']
        self.tax_sky_url = config['link']['tax_sky_url']
        self.bank_update_url = config['link']['bank_update_url']
        # 残疾人保障金申报信息获取地址
        self.new_tax_url = config['link']['new_tax_url']
        self.tax_update_url = config['link']['tax_update_url']
        self.sb_url = config['link']['sb_data_url']

        # # 税务扣款页面地址
        self.tax_kk_page_url = config['link']['tax_kk_page_url']
        # 社保扣款地址
        self.sb_kk_page_url = config['link']['sb_kk_page_url']
        # 税务扣款获取数据列表接口地址
        self.tax_kk_url = config['link']['tax_kk_url']
        # 社保扣款获取数据列表接口地址
        self.sb_kk_url = config['link']['sb_kk_url']
        # 获取网银接口
        self.net_bank_url = config['link']['net_bank_url']
        # 税务扣款提交接口地址
        self.tax_kk_submit_url = config['link']['tax_kk_submit_url']
        # 社保扣款提交接口地址
        self.sb_kk_submit_url = config['link']['sb_kk_submit_url']
        # 系统未扣款客户
        self.tax_kk_info_url = config['link']['tax_kk_info_url']
        # 提交扣款结果
        self.tax_kk_sb_url = config['link']['tax_kk_sb_url']
        # 获取已扣款数据
        self.kk_update_url = config['link']['kk_update_url']

        # 系统未报税客户
        self.tax_report_info_url = config['link']['tax_report_info_url']
        # 报税所需数据接口
        self.tax_export_data_url = config['link']['tax_export_data_url']
        # 批量更新扣款数据接口
        self.bundle_kk_status_url = config['link']['bundle_kk_status_url']
        # 待上传税务报表客户
        self.ready_sw_url = config['link']['ready_sw_url']

        # 报税，社保申报结果上传
        self.sb_auto_ret_url = config['link']['sb_auto_ret_url']
        # 社保网站缴纳详情接口
        self.sb_jk_list_url = config['link']['sb_jk_list_url']
        # 社保待上传详情信息
        self.ready_sb_jk_detail_url = config['link']['ready_sb_jk_detail_url']
        # 社保详情上传接口
        self.sb_jk_detail_upload_url = config['link']['sb_jk_detail_upload_url']

        # 需要获取代开具发票的企业
        self.agent_ready_url = config['link']['agent_ready_url']
        # 获取代开具发票
        self.zzfp_detail_url = config['link']['zzfp_detail_url']
        self.dkfp_detail_url = config['link']['dkfp_detail_url']
        self.dkfp_data_url = config['link']['dkfp_data_url']
        # 代开具发票信息上传
        self.agent_invoice_url = config['link']['agent_invoice_url']
        # 代开具发票详情上传
        self.agent_invoice_detail_url = config['link']['agent_invoice_detail_url']
        # 代开发票报税所需数据
        self.agent_list_url = config['link']['agent_list_url']
        # debug配置
        self.show_browser = config['debug']['browser_show']

        self.template = config['tax_template']
        self.tax_config_info = config['tax_config_info']
        # self.status_bar = status_bar

    def set_corp(self,corp_list):
        self.insert_log('') 
        self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action= corp_list.split('||',7)
        self.insert_log("执行请求:"+self.corpname + " " + self.action)
        return self.corpid

    #打开浏览器
    def open_browser(self):
        chrome_options = Options()

        tmp_path = regedit.get_client_path()
        # 配置chrom浏览器默认保存文件路径
        prefs = {'profile.default_content_settings.popups': 0, #防止保存弹窗
        'download.default_directory':tmp_path,#设置默认下载路径
        "profile.default_content_setting_values.automatic_downloads":1#允许多文件下载
        }
        chrome_options.add_experimental_option('prefs', prefs)
        #修改windows.navigator.webdriver，防机器人识别机制，selenium自动登陆判别机制
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) 

        # 根据配置是否显示浏览器
        if self.show_browser == '0':
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.maximize_window()
        
     #登录
    def login(self):
        driver = self.driver
        driver.get(self.login_url)

        #跳过引导
        sleep(3)
        # guide_jump_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,'neverGuide'))).click()
        #guide_jump_btn.click()
        #Action = ActionChains(driver)# 实例化一个action对象
        #guide_jump_btn = driver.find_element_by_id("neverGuide")#跳过引导按钮
        #guide_jump_action = Action.click(guide_jump_btn)#点击
        #guide_jump_action.perform()
        # 尝试登录6次
        return self.login_action(3)


    # 重复尝试登录        
    def login_action(self,login_times):
        driver = self.driver
        htool = HTool()
        if login_times == 0:
            self.taxObj.remove_task()
            htool.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'1','msg':'登录失败次数过多'})
            driver.quit()
            return False
        login_times -= 1
        
        try:
            #打开登录框
            Action = ActionChains(driver)# 实例化一个action对象
            login_open = driver.find_element_by_id("login")#获取打开登录框的按钮
            login_open_click = Action.click(login_open)#点击
            login_open_click.perform()
            sleep(1)
            # driver.execute_script('init.openLoginView()')
            
            # driver.switch_to.frame("loginSrc")#切换到登录框iframe
            tax_code_input = driver.find_element_by_id("username")
            pwd_input = driver.find_element_by_id("password")
            verify_code = driver.find_element_by_xpath("//form[@id='fm3']/div/input[@name='yzm']")
            # slide_box = driver.find_element_by_id("vc1")
            # slide_btn = driver.find_element_by_xpath("//form[@id='fm2']/div/div/div/div[@class='sliderVc_button']")
            login_btn = driver.find_element_by_xpath("//form[@id='fm3']/div/button[@class='button fr']")
            tax_code_input.send_keys(self.credit_code)
            pwd_input.send_keys(self.pwd)
            parse_code = self.parse_action()
            verify_code.send_keys(parse_code)
            #点击登录
            login_btn_click = Action.click(login_btn)
            login_btn_click.perform()
            sleep(4)
            # 判断是否有密码错误的提示框出来 
            pass_err = driver.find_element_by_class_name("layui-layer-dialog")
            if pass_err:
                err_msg = pass_err.find_element_by_xpath("./div[@class='layui-layer-content']").text
                print(err_msg)
                if '您的密码已输错' in err_msg or '密码输入错误' in err_msg or '锁定' in err_msg or '请输入密码' in err_msg or '企业户账号不存在' in err_msg:
                    self.insert_log("报税密码错误，请及时修改")
                    # 密码错误
                    htool.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'0','msg':'报税密码错误，请及时修改'})
                    if self.action in ['7','8']:
                        post_data = {"corpid":self.corpid,"jkrqq":time.strftime("%Y-%m-01",time.localtime()),"jkrqz":time.strftime("%Y-%m-%d",time.localtime()),"json_data":"","msg":err_msg}
                        htool.post_data(self.bundle_kk_status_url,post_data)
                    elif self.action == '10':
                        htool.post_data(self.agent_invoice_detail_url,{"corpid":self.corpid,"msg":"报税密码错误，请及时修改","rows_data":"[]"})
                    self.taxObj.remove_task()
                    driver.quit()
                    return False
                # 如果是计算结果错误,可重试
                if '结果输入有误' in err_msg:
                    self.insert_log("验证码识别结果不正确，请等待")
                    # self.taxObj.remove_task()
        except Exception as e:
            print(e)
        
        # 判断是否登录成功
        try:
            driver.execute_script('layer.closeAll()')
            login_open = driver.find_element_by_id("login")
            if login_open:
                print('登录失败，重新登录')
                print('login_times',login_times)
                return self.login_action(login_times)
        except Exception as e:
            print(e)
        try:
            self.driver.execute_script("$_ajax({url: url_kqxx,success: function(c) {fuser['uuid']=c[0].DJXH;}});")
            sleep(1)

            self.fuser = self.driver.execute_script("return fuser;")
            if 'uuid' not in self.fuser:
                self.fuser['uuid'] = ''
        except Exception as e:
            print('获取用户信息失败',e)
            return False
        return True



    # 解析验证码，直到获取到一个结果为止        
    def parse_action(self):
        #保存验证码图片到本地 并识别
        htool = HTool()
        local_img = htool.save_ercode_img(self.driver,"//form[@id='fm3']/div//div/img")
        res = htool.send_img(local_img)

        if res['parse']:
            return res['parse']
        else:
            print('解析验证码失败，重新解析')
            sleep(2)
            return self.parse_action()


    #登录后页面初始化
    def page_init(self):
        sleep(3)
        driver = self.driver
        Action = ActionChains(driver)# 实例化一个action对象
        try:
            close_layer_btn = driver.find_element_by_class_name("layui-layer-close")
            close_layer = Action.click(close_layer_btn)#关闭弹窗
            close_layer.perform()
        except Exception as e:
            print('登录页面初始化失败',e)


    # 执行操作
    def driver_auto_action(self):
        ac = self.action.split('+')
        for a in ac:
            # if a == '1':
            #     msg.append(self.syn_user_total())
            if a == '2':
                self.insert_log('更新登记信息')
                self.get_comp_info()
            if a == '3':
                self.insert_log('更新税费（种）认定信息')
                self.get_tax_info()
            if a == '4':
                self.insert_log('更新银行登记信息')
                self.get_bank_info()
            if a == '5':
                self.insert_log('更新报税信息')
                self.get_tax_detail()
            if a == '6':
                self.insert_log('更新社保信息')
                self.get_sb_detail()
            if a == '7':
                self.insert_log('税款缴纳并更新扣款状态')
                self.do_tax_kk()
            if a == '8':
                self.insert_log('更新扣款状态')
                self.update_kk_info()
            if a == '9':
                self.insert_log('税务申报')
                self.tax_sb()
                self.social_insurance()
            if a == '10':
                self.insert_log('获取税务局代开具发票')
                self.sw_dkfp_search()
            if a == '11':
                self.insert_log('获取社保信息')
                self.tax_si_upload()
            if a == '12':
                self.insert_log('获取信诺网代开发票')
                self.xnw_dkfp_search()
        print('执行任务结束',a)        
        self.driver.quit()

    # 公司登记信息
    def get_comp_info(self):
        ret_msg = '获取登记信息失败'
        htool = HTool()
        try:
            comp = htool.get_data(self.comp_info_url,self.driver)
            if comp:
                soup = BeautifulSoup(comp.text,'lxml')
                form_node = soup.select('.form-group')
                rt_dict = {}
                for node in  form_node:
                    k = node.find('label').get_text()
                    k = ChToWod.getPinyin(k)
                    v = node.find('input')['value']
                    rt_dict[k] = v
                # print(rt_dict)

                print('上传申报统计数据')
                syn_res = htool.post_data(self.tax_corp_info_url,{'info':str(rt_dict),'corpid':self.corpid})
                if syn_res.status_code == 200:
                    ret_msg = '获取登记信息成功'
        except Exception as e:
            print(e)
        return ret_msg

    # 税费（种）认定信息 
    def get_tax_info(self):
        ret_msg = '获取税费（种）认定信息失败'
        htool = HTool()
        try:
            tax_info = htool.get_data(self.tax_info_url,self.driver)
            if tax_info:
                tax_node = BeautifulSoup(tax_info.text,'lxml')
                tax_array = tax_node.find(id='tableTest2').find('tbody').find_all('tr')
                rt_dict = []

                for node in tax_array:
                    td_arr = node.get_text().strip('\n')
                    rt_dict.append(td_arr.split('\n'))

                print('税费（种）认定信息')
                print(rt_dict)
                syn_res = htool.post_data(self.tax_confirm_info_url,{'info':str(rt_dict),'corpid':self.corpid})
                if syn_res.status_code == 200:
                    ret_msg = '获取税费（种）认定信息成功'
        except Exception as e:
            print('获取税费种信息失败',e)
        return ret_msg

    # 检查当前关键词是否都在模板里匹配
    def check_keyword_in_temp(self,k,temp):
        k_arr = k.split("&")
        match_row = True
        for keyword in k_arr:
            if keyword not in temp:
                match_row = False
                break    
        return match_row    

    def get_tax_detail(self):
        htool = HTool()
        data = {'sbrqq': self.sbrqq, 'sbrqz': self.sbrqz,'uuid':self.fuser['uuid']}
        ret_msg = '获取申报统计数据失败'
        try:
            sb_data = htool.post_data(self.tax_data_url,data,self.driver)
            # print('获取详情结果',sb_data.text)
        except Exception as e:
            print('获取已申报信息失败',e)
            return False

        if sb_data and sb_data.status_code == 200:
            try:
                # print('统计数据结果',sb_data.text)
                tax_json = json.loads(sb_data.text)
            except Exception as e:
                print(e)
                self.insert_log(self.corpname+": 获取申报数据失败,解析统计数据页面出错")
                return False
            
            rt = []
            
            # 解析title的模板
            parse_common_temp = json.loads(self.template['common'])
            load_config = json.loads(self.template['template'])
            try:
                # 解析统计数据，获取详情与解析模板
                for d in tax_json['data']:
                    print(d['YZPZZL_DM'],d['YZPZZL_MC'])
                    qmldse = 0
                    if '一般纳税人适用' in d['YZPZZL_MC']:
                        link = htool.open_cell(d)
                        sb_data = htool.get_data(link,self.driver)
                        # print(sb_data.text)
                        qmld_match = re.search(r'"qmldse":"(\d{0,}\.?\d{0,})"',sb_data.text)
                        if qmld_match:
                            qmldse = qmld_match.group(0).replace('"qmldse":"','').replace('"','')
                        else:
                            qmldse = 0
                    # 匹配模板关键词找到解析模板
                    parse_match_temp = {}
                    parse_common_data = {"qmldse":qmldse}
                    for temp in load_config:
                        if self.check_keyword_in_temp(temp['keyword'],d['YZPZZL_MC']):
                            
                            # 解析详情的模板
                            parse_match_temp = temp
                            break
                    # 解析统计部分通用数据
                    for common in parse_common_temp:
                        parse_common_data[common] = d[parse_common_temp[common]]
                    link = htool.open_cell(d)
                    # 过滤掉无连接的数据
                    if self.check_detail_link(d['YZPZZL_MC']):
                        parse_common_data['sheet_detail_link'] = link
                    # print('详情链接',link,parse_match_temp)
                    if parse_match_temp:
                        # 获取报税详情
                        sb_data = htool.get_data(link,self.driver)
                        if sb_data.status_code == 200:
                            # 残疾保障金页面数据需要提交form跳转页面获取
                            # if parse_match_temp['temp_id'] == '3':
                            #     sb_data = self.new_tax_page(sb_data.text)
                            
                            initData = re.search(r''+parse_match_temp['re_match_name']+'.{10,};',sb_data.text).group(0)
                            initData = initData.replace(parse_match_temp['re_match_name'],'').strip("\";'")
        
                            row_detail = self.parseTax(initData,parse_match_temp,parse_common_data)
                        # print(row_detail)
                        else:
                            print(sb_data.text)
                        rt.append(row_detail)
                    else:
                        cat_add = True
                        row_detail = self.parseTaxRaw(d,parse_common_data)
                        rt.append(row_detail)
                        ignore = self.template['ignore'].split(',')
                        for i in ignore:
                            if i in d['YZPZZL_MC']:
                                cat_add = False
                                break
                        if cat_add:
                            self.insert_log("待解析的税种模板(%s)不存在！请注意及时添加" % d['YZPZZL_MC'])
                            pass
            

                ss_data = self.ss_gl(rt)
                qmldse = 0
                for ss_item in ss_data:
                    fill_date_arr = ss_item.split('-')
                    fill_date = "%s-%s-01" % (fill_date_arr[0],fill_date_arr[1])

                    stop_date_arr = ss_data[ss_item][0]['stop_date'].split('-')
                    period = "%s%s" % (stop_date_arr[0],stop_date_arr[1])

                    for i in ss_data[ss_item]:
                        qmldse += float(i['qmldse'])
                    # print(ss_data[ss_item])
                    res = htool.post_data(self.tax_update_url,{"corpid":self.corpid,'period':period,'tax_type':0,'qmldse':qmldse,'fill_date':fill_date,"msg":"自动更新[所属期：%s - 已申报税收数据]完成 期末留抵税额:%s" % (period,qmldse),"data":json.dumps(ss_data[ss_item])})
                    print('申报结果',res.text)
                    if res.status_code == 200:
                        res_text = json.loads(res.text)
                        if res_text['code'] != 0:
                            ret_msg = res_text['text']
                            self.insert_log(res_text['text'])
                        else:
                            return True    
                    else:
                        self.insert_log('上传税收数据时发生了一个错误')
            except Exception as e:
                print(e)
                self.insert_log(ret_msg)
                # pahtool.post_data(self.tax_update_url,{"corpid":self.corpid,'period':period,'fill_date':sbrqz,"msg":"解析上传[%s-%s]已申报数据失败" % (sbrqq,sbrqz),"data":'[]'})ss
            return False
        else:
            print(sb_data.text)
            htool.post_data(self.tax_update_url,{"corpid":self.corpid,'period':period,'tax_type':0,'fill_date':self.sbrqz,'qmldse':qmldse,"msg":"从税务局网站获取[%s-%s]已申报数据失败" % (self.sbrqq,self.sbrqz),"data":'[]'})
        self.insert_log(ret_msg)
        
        return False

    # 税收数据归类
    def ss_gl(self,ss_list):
        # print(sl_data)
        gl_dict = {}
        for ss in ss_list:
            fill_date_arr = ss['fill_date'].split('-')
            fill_date = "%s-%s-01" % (fill_date_arr[0],fill_date_arr[1])
            if fill_date in gl_dict:
                 gl_dict[fill_date].append(ss)
            else:
                gl_dict[fill_date] = [ss]

        return gl_dict

    # 检查是否有详情链接
    def check_detail_link(self,sub_title):
        no_detail_link = self.template['no_link']
        has_link = True
        no_link_arr = no_detail_link.split(',')
        for li in no_link_arr:
            if li in sub_title:
                has_link = False
                break
        return has_link

    # 解析页面form参数，获取新版纳税申报页面数据
    # def new_tax_page(self,parse_html):
    #     html_node = BeautifulSoup(parse_html,'lxml')
    #     form_node = html_node.find(id="submitForm").find_all('input')
    #     submit_form = {}
    #     for i in form_node:
    #         submit_form[i['name']] = i['value']
    #     new_page = htool.post_data(self.new_tax_url,submit_form)
    #     return new_page

    # 解析单条统计数据并返回
    def parseTaxRaw(self,data,parse_common_data):
        parse_common_data['bqynse'] = data['YBTSE']
        parse_common_data['bqybtse'] = data['YBTSE']
        parse_common_data['bqyjse'] = 0
        parse_common_data['json_detail'] = json.dumps(parse_common_data)
        return parse_common_data

     # 解析单条申报数据
    def parseTax(self,data,template,parse_common_data):
        try:
            # print(data)
            json_data = json.loads(data)
        except:
            self.insert_log("解析json数据错误 %s" % data)
            return[]

        # 通用模板
        match_rows = []
        return_data = []
        if template['temp_id'] == '1':
            if 'fxmtysbbdVO' in json_data:
                match_rows = json_data['fxmtysbbdVO']['fxmtySbb']['sbxxGrid']['sbxxGridlb']
                if type(match_rows) == dict:
                    match_rows = [match_rows]
            elif 'sb_fxmtysb' in json_data:
                match_rows = json_data['sb_fxmtysb']
            else:
                self.insert_log('解析通用数据json错误')
                print(data)
                sys.exit()
        # 印花税json 
        if template['temp_id'] == '2':
            if 'yyssbbdxxVO' in json_data:
                match_rows = json_data['yyssbbdxxVO']['yhssb']['yhssbGrid']['yhssbGridlb']
            elif 'yhssbywbw' in json_data:
                match_rows = json_data['yhssbywbw']['yhssb']['slrxxForm']
            elif 'sb_yhs' in json_data:
                match_rows = json_data['sb_yhs']
            else:
                self.insert_log("未找到解析印花税的方法，请及时检查")
                # print(data)
            if type(match_rows) == dict:
                match_rows = [match_rows]

        # 企业所得税B类json
        if template['temp_id'] == '3':
            if 'sb_sds_jmhd_18yjnd' in json_data:
                match_rows = json_data['sb_sds_jmhd_18yjnd']
            else:
                self.insert_log("未找到解析B类报表的方法 %s" % data)
            if type(match_rows) == dict:
                match_rows = [match_rows]

            # print(match_rows)    
            parse_common_data['type'] = 'B'
                
        # 附加税json
        if template['temp_id'] == '4':
            if 'fjsSbbdxxVO' in json_data:
                match_rows = json_data['fjsSbbdxxVO']['fjssbb']['sbxxGrid']['sbxxGridlbVO']
            elif 'sb_nsrjbxx' in json_data:
                match_rows = json_data['sb_fjsf']
            elif 'fjssbbw' in json_data:
                match_rows = json_data['fjssbbw']['fjssbb']['sbxxGrid']['sbxxGridlbVO']
            else:
                self.insert_log("未找到解析附加税数据的方法 %s" % data)
            
            if type(match_rows) == dict:
               match_rows = [match_rows]

        # 企业所得税A类json
        if template['temp_id'] == '5':
            if 'qysdsczzsyjdSbbdxxVO' in json_data:
                match_rows = json_data['qysdsczzsyjdSbbdxxVO']['A200000Ywbd']['sbbxxForm']
            elif 'sb_sds_jmcz_18yjd' in json_data:
                match_rows = json_data['sb_sds_jmcz_18yjd']
            else:
                self.insert_log("未找到解析A类报表的方法 %s" % data)
            if type(match_rows) == dict:
                match_rows = [match_rows]
            parse_common_data['type'] = 'A'
                

        # 解析增值税纳税 json
        if template['temp_id'] == '6' or template['temp_id'] == '7':
            if 'taxML' in json_data:
                data_rows = json_data['taxML']['zzsybsbSbbdxxVO']['zzssyyybnsr_zb']['zbGrid']['zbGridlbVO']
            elif 'sb_zzs_ybnsr' in json_data:
                data_rows = json_data['sb_zzs_ybnsr']
            elif 'zzssyyxgmnsrySbSbbdxxVO' in json_data:
                data_rows = json_data['zzssyyxgmnsrySbSbbdxxVO']['zzssyyxgmnsr']['zzsxgmGrid']['zzsxgmGridlb']
            elif 'sb_zzs_ybnsr' in json_data:
                data_rows = json_data['sb_zzs_ybnsr']
            elif 'sb_zzs_xgm' in json_data:
                data_rows = json_data['sb_zzs_xgm']
            else:
                self.insert_log("未找到解析增值税纳税的方法 %s" % data)

            if type(match_rows) == dict:
                data_rows = [data_rows]

            parse_table = {}
            parse_data = {}
            for match in template['sub_title']:
                sub_index = 0
                data_row = {}
                for sub in template['sub']:
                    # 更新解析模板与数据
                    data_row[sub] = data_rows[sub_index].get(match,'')
                    sub_index += 1
                parse_data[match] = data_row
            parse_table["table"] = parse_data

            parse_json = dict(parse_table , **parse_common_data)
            return_data.append(parse_json)


        # 解析匹配的详情数据（json格式的）
        for match_row in match_rows:
            # parse_common_data 为可解析的通用数据
            parse_data = {}
            for f in template['match']:
                try:
                    match_array = template['match'][f].split('|')

                    parse_data[f] = ''
                    for match_key in match_array:
                        match_val = match_row.get(match_key,'')
                        if match_val:
                            parse_data[f] = match_val
                           
                except:
                    self.insert_log('解析详情数据失败')
                    pass
            parse_data = dict(parse_common_data,**parse_data)
            return_data.append(parse_data)

        parse_common_data['json_detail'] = json.dumps(return_data)
        return parse_common_data

    def get_sb_detail(self,all_month = True):
        sb_list = []
        htool = HTool()
        err_msg,sb_list = self.get_sb_all(self.sbrqq,self.sbrqz,sb_list,all_month)
        
        if err_msg != '':
            return err_msg
        
        if len(sb_list) == 0:
            return True
        else:
            # 数据重新归类
            print('数据重新归类')
            sb_list = self.sb_gl(sb_list)

        for sb_period in sb_list:
            sb_list[sb_period]['json_detail'] = '['+','.join(sb_list[sb_period]['json_detail'])+']'
            # print(sb_list[sb_period])
            print('上传社保结果',[sb_list[sb_period]])
            res = htool.post_data(self.tax_update_url,{"corpid":self.corpid,'period':sb_list[sb_period]['period'],'tax_type':1,'fill_date':sb_list[sb_period]['fill_date'],"msg":"自动更新[所属期：%s - 已申报社保数据]完成" % sb_list[sb_period]['period'],"data":json.dumps([sb_list[sb_period]])})
            if res.status_code == 200:
                try:
                    res_text = json.loads(res.text)
                    if res_text['code'] != 0:
                        print(self.corpname+":获取社保信息失败 "+res_text['text'])
                        return False
                except: 
                    return False
            else:
                return False
        return True        

    # 社保数据归类
    def sb_gl(self,sb_list):
        gl_dict = {}
        for sb in sb_list:
            fill_date_arr = sb['fill_date'].split('-')
            fill_date = "%s-%s-01" % (fill_date_arr[0],fill_date_arr[1])

            stop_date_arr = sb['stop_date'].split('-')
            period = "%s%s" % (stop_date_arr[0],stop_date_arr[1])
            if fill_date in gl_dict:
                gl_dict[fill_date]['period'] = period
                gl_dict[fill_date]['bqybtse'] += float(sb['bqybtse'])
                gl_dict[fill_date]['bqynse'] += float(sb['bqynse'])
                gl_dict[fill_date]['json_detail'].append(json.dumps(sb))
            else:
                gl_dict[fill_date] = {"categories_name":"社保","voucher_number":sb['voucher_number'],"period":period,"start_date":sb['start_date'],"stop_date":sb['stop_date'],'fill_date':sb['fill_date'],"bqybtse":float(sb['bqybtse']),"bqynse":float(sb['bqynse']),"json_detail":[json.dumps(sb)]}

        return gl_dict

    # 递归获取时间范围内所有申报
    def get_sb_all(self,sbrqq,sbrqz,sb_list,all_month=True):
        # 获取单位核定申报与单位自主申报数据
        htool = HTool()
        if all_month == True:
            rel_sbrqq,rel_sbrqz,end = htool.split_time(sbrqq,sbrqz)
        else:
            rel_sbrqq = sbrqq
            rel_sbrqz = sbrqz 
            end = True
        for i in range(0,2):
            data = {'sbrqq': rel_sbrqq, 'sbrqz': rel_sbrqz,'sbbzlDm':i}
            ret_msg = '获取社保信息失败'
            try:
                # print('获取数据',rel_sbrqq,rel_sbrqz)
                sb_data = htool.post_data(self.sb_url,data,self.driver)
            except:
                return ret_msg,sb_list
            
            if sb_data and sb_data.status_code == 200:
                try:
                    tax_json = json.loads(sb_data.text)
                    # print('获取数据',rel_sbrqq,rel_sbrqz,tax_json)
                    if tax_json['code'] != 200:
                        return tax_json['error']['errorMsgs'][0],sb_list
                    if len(tax_json['data']) > 0:
                        sb_list = sb_list + self.parse_sb_detail(tax_json['data'])
                        
                    if end == False and i == 1:
                        return self.get_sb_all(rel_sbrqz,self.sbrqz,sb_list)
                    if end == True and i == 1:
                        return '',sb_list
                except:
                    return ret_msg,sb_list
            else:
                return ret_msg,sb_list

    # 解析社保详情
    def parse_sb_detail(self,sb_data):
        parse_common_temp = json.loads(self.template['sb_common'])
        htool = HTool()
        parse_row = []
        for d in sb_data:
            parse_common_data = {}
            for common in parse_common_temp:
                parse_common_data[common] = d[parse_common_temp[common]]
            parse_common_data['categories_name'] = '社保-' + parse_common_data['categories_name']
            link = htool.open_cell(d)
            parse_common_data['sheet_detail_link'] = link
            if self.template['sb_fee_num'] in d['ZSPMMC']:
                parse_common_data['json_detail'] = self.get_sb_fee_num(link)
            parse_row.append(parse_common_data)
        return parse_row

    # 获取社保核定人数
    def get_sb_fee_num(self,link):
        htool = HTool()
        sb_data = htool.get_data(link,self.driver)
        
        re_match_str = 'initData = '
        initData = re.search(r''+re_match_str+'.{10,};',sb_data.text).group(0)
        initData = initData.replace(re_match_str,'').strip("\";'")
        parse_json = json.loads(initData)

        if 'ShbxfStandardZxsbDetailList' in parse_json:
            parse_data = parse_json['ShbxfStandardZxsbDetailList']['ShbxfStandardZxsbDetail']
        elif 'ShbxfStandardHdsbDetailList' in parse_json:
            parse_data = parse_json['ShbxfStandardHdsbDetailList']['ShbxfStandardHdsbDetail']
        else:
            print('未找到解析社保json数据的方法')
            return {}

        for d in parse_data:
            # 兼容处理，品目名称不一致问题
            cate_name = d.get('ZSPM_MC')
            if cate_name == None:
                cate_name = d.get('zspm_mc')
            if self.template['sb_fee_num'] in cate_name:
                return json.dumps({"jfrs":d['jfrs']})

    # 获取期末留抵数据
    def get_qmld(self,sb_data):
        # link = self.open_cell(self.tax_data)
        # print(link)
        # sb_data = htool.post_data(self.tax_data_url,{'sbrqq':'2018-11-01','sbrqz':'2019-10-14'})
        htool = HTool()
        if(sb_data):
            tax_json = json.loads(sb_data.text)
            rt = []
            for d in tax_json['data']:
                if '一般纳税人适用' in d['YZPZZL_MC']:
                    link = htool.open_cell(d)
                    sb_data = htool.get_data(link,self.driver)
                    # print(sb_data.text)
                    qmld_match = re.search(r'"qmldse":"(\d{0,}\.?\d{0,})"',sb_data.text)
                    if qmld_match:
                        d['qmldse'] = qmld_match.group(0).replace('"qmldse":"','').replace('"','')
                    else:
                         d['qmldse'] = 0
                rt.append(d)
        return rt

    # 获取银行备案信息
    def get_bank_info(self):
        ret_msg = '获取银行登记信息失败'
        htool = HTool()
        try:
            bank_info = htool.get_data(self.tax_sky_url,self.driver)
            post_res = []
            if bank_info:
                bank_node = BeautifulSoup(bank_info.text,'lxml')
                
                if bank_node.find(class_='panel') == None:
                    return '暂无银行登记信息'
                bank_array = bank_node.find(class_='panel').find_all(class_='panel-body')
                rt_bank = []
                for b in bank_array:
                    form_group = b.find_all(class_='form-group')
                    parse ={}
                    for arr in form_group:
                        k = arr.find('label').text
                        v = arr.find(class_='as-bgf')['value']
                        parse[ChToWod.getPinyin(k)] = v
                    rt_bank.append(parse)
                post_res = htool.post_data(self.bank_update_url,{"corpid":self.corpid,"bank_list":str(rt_bank)})
                if post_res.status_code == 200:
                    ret_msg = '更新银行登记信息成功'
            print(str(rt_bank))

        except:
            pass
        return ret_msg

    # 税款缴纳
    def do_tax_kk(self):
        htool = HTool()
        # 获取缴款账户，如果没有账户直接跳过，如果有多个
        bank_data = htool.post_data(self.net_bank_url,{},self.driver)
        self.taxObj.remove_task()

        if bank_data.status_code == 200:
            tbrq = time.strftime("%Y-%m-01",time.localtime())
            kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":"","tbrq":tbrq,"ssqq":"","ssqz":"","kk_item_name":"","msg":""}
            try:
                bank_json = json.loads(bank_data.text)
                bank_num = len(bank_json['data'])
                if bank_num == 0:
                    ret_msg = '未添加扣款网银账户，扣款失败'
                    # kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":"","ssqq":"","ssqz":"","kk_item_name":"","msg":ret_msg}
                    kk_post_data['msg'] = ret_msg
                    pos_ret = htool.post_data(self.tax_kk_sb_url,kk_post_data)
                    print(pos_ret.text)
                    
                    return ret_msg
            except Exception as e:
                print('获取税费银信息时出错',e)
                ret_msg = '解析待扣款数据出错，请手动登录网站检查'
                # kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":"","ssqq":"","ssqz":"","kk_item_name":"","msg":ret_msg}
                kk_post_data['msg'] = ret_msg
                htool.post_data(self.tax_kk_sb_url,kk_post_data)
                return ret_msg

        else:
            ret_msg = '获取扣款账户失败'
            print(ret_msg,bank_data.text)
            return ret_msg

        # 税务扣款信息
        # print('扣除企业或个税税款')
        self.driver.get(self.tax_kk_page_url)
        # print('打开扣款界面')
        sleep(5)
        tax_kk_ret = self.do_tax_kk_action(bank_num)
        # print('扣款上传结果',tax_kk_ret)
        self.insert_log(tax_kk_ret['msg'])
        htool.post_data(self.tax_kk_sb_url,tax_kk_ret)
        # 如果税费扣款失败，直接退出
        if tax_kk_ret['kk_status'] == 2:
            return tax_kk_ret['msg']

        # 社保扣款
        print('扣除社保税款')
        self.driver.get(self.sb_kk_page_url)
        sb_kk_ret = self.do_sb_kk_action(bank_num)
        htool.post_data(self.tax_kk_sb_url,sb_kk_ret)
        # print("社保扣款提交结果",sb_kk_ret)


        jkrqq = time.strftime("%Y-%m-01",time.localtime())
        jkrqz = time.strftime("%Y-%m-%d",time.localtime())
        self.update_kk_info(jkrqq,jkrqz)
        return sb_kk_ret['msg'] + ',' + tax_kk_ret['msg']

    # 社保缴纳
    def do_sb_kk_action(self,bank_num):
        htool = HTool()
        # 获取缴款信息
        kk_data = htool.post_data(self.sb_kk_url,{},self.driver)
        tbrq = time.strftime("%Y-%m-01",time.localtime())
        kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":"","tbrq":tbrq,"ssqq":"","ssqz":"","kk_item_name":"","msg":""}

        # 获取页面中待扣款个数
        if kk_data.status_code == 200:
            kk_json = json.loads(kk_data.text)
            # print('社保扣款',kk_json)
            # print('社保信息',kk_json)
            kk_item_num = len(kk_json['data'])
        else:
            kk_post_data['msg'] = '扣款失败,获取社保费缴纳信息时发生错误'
            return kk_post_data

        if kk_item_num == 0:
            kk_post_data['kk_status'] = 1
            kk_post_data['msg'] = '扣款成功,社保费缴纳信息为空'
            return kk_post_data

        sleep(5)
        bank_select = str(bank_num - 1)
        self.driver.execute_script("$('input[name=btSelectAll]').click();$('#sfxyTable input[name=btSelectItem]').eq("+bank_select+").attr('checked',true);$('#sfxyTable input[name=btSelectItem]').eq("+bank_select+").click()")
        kk_submit_data = self.driver.execute_script("oneCheckFormData();return getTjsj()")

        parse = {}
        js_arr = kk_submit_data.split('&')
        for i in js_arr:
            sp_arr = i.split('=')
            parse[sp_arr[0]] = sp_arr[1]

        # 通过应征凭证序号找到缴款项目
        kk_name_arr = []
        ssqq = ssqz = ''
        for item in kk_json['data']:
            ssqq = item['SKSSQQ']
            ssqz = item['SKSSQZ']
            tax_code = item['YZPZZL_DM']
            if 'SBRQ_1' in item:
                tbrq = item['SBRQ_1']
            kk_name_arr.append(item['ZSXMMC'])

        kk_item_name = '、'.join(kk_name_arr)
        # 对接接口提交数据
        kk_post_data['tax_code'] = tax_code
        kk_post_data['ssqq'] = ssqq
        kk_post_data['ssqz'] = ssqz
        kk_post_data['tbrq'] = tbrq
        kk_post_data['kk_item_name'] = kk_item_name
        # kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":tax_code,"skssqq":ssqq,"skssqz":ssqz,"zsxmMc":kk_item_name,"msg":""}
        # print('kk_post_data',kk_post_data,parse)

        kk_submit_data = kk_submit_data.replace("+", "%2B")
        # print('社保提交数据',kk_submit_data)
        kk_ret = htool.post_data(self.sb_kk_submit_url,kk_submit_data.encode("utf-8"),self.driver,{"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"})
        if kk_ret.status_code == 200:
            kk_json = json.loads(kk_ret.text)
            print('扣款结果',kk_json)
            if kk_json['code'] == 200:
                # 扣款成功,继续扣款
                kk_post_data['msg'] = kk_item_name+',扣款成功'
                kk_post_data['kk_status'] = 1
                self.insert_log(kk_item_name+',扣款成功')
            else:
                # 多个账户时可以轮流扣款
                if bank_num > 1:
                    bank_num -= 1
                    self.driver.execute_script("window.location.reload()")
                    return self.do_sb_kk_action(bank_num)
                else:
                    err_msg = '扣款失败，['+kk_item_name+'] '+kk_json['error']['errorMsgs'][0]
                    kk_post_data['msg'] = err_msg
                    self.insert_log(err_msg)
        else:            
            err_msg = kk_item_name+'提交扣款信息失败'
            self.insert_log(err_msg)
            kk_post_data['msg'] = err_msg
        return kk_post_data

    # 税款缴纳循环扣款，直到所有账户失败停止
    def do_tax_kk_action(self,bank_num):
        htool = HTool()
        # 获取扣款数据
        data = {'swjgdm': '13401030000'}
        kk_data = htool.post_data(self.tax_kk_url,data,self.driver)
        tbrq = time.strftime("%Y-%m-01",time.localtime())
        kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":"","ssqq":"","tbrq":tbrq,"ssqz":"","kk_item_name":"","msg":""}
        
        # 获取页面中待扣款个数
        if kk_data.status_code == 200:
            kk_json = json.loads(kk_data.text)
            kk_item_num = len(kk_json['data'])
        else:
            kk_post_data['msg'] = '扣款失败,获取未缴款信息时发生错误'
            return kk_post_data

        if kk_item_num == 0:
            kk_post_data['kk_status'] = 1
            kk_post_data['msg'] = '扣款成功,税费缴纳信息为空'
            return kk_post_data

        sleep(5)
        bank_select = str(bank_num - 1)
        self.driver.execute_script("$('input[name=btSelectItem]').click();$('#sfxyTable input[name=btSelectItem]').eq("+bank_select+").click()")
        kk_submit_data = self.driver.execute_script("oneCheckFormData();return getTjsj()")

        parse = {}
        js_arr = kk_submit_data.split('&')
        for i in js_arr:
            sp_arr = i.split('=')
            parse[sp_arr[0]] = sp_arr[1]
        # print('扣款提交数据',parse)

        # 通过应征凭证序号找到缴款项目
        kk_name_arr = []
        ssqq = ssqz = tax_code =  ''
        for item in kk_json['data']:
            # print('报税item',item)
            if item['yzpzxh'] == parse['yzpzxh']:
                ssqq = item['skssqq']
                ssqz = item['skssqz']
                tax_code = item['yzpzzlDm']
                kk_name_arr.append(item['zsxmMc'])
            if 'nssbrq' in item:
                tbrq = item['nssbrq']

        kk_item_name = '、'.join(kk_name_arr)
        # 对接接口提交数据
        kk_post_data['tax_code'] = tax_code
        kk_post_data['ssqq'] = ssqq
        kk_post_data['ssqz'] = ssqz
        kk_post_data['tbrq'] = tbrq
        kk_post_data['kk_item_name'] = kk_item_name
        # kk_post_data = {"corpid":self.corpid,"kk_status":2,"tax_code":tax_code,"skssqq":ssqq,"skssqz":ssqz,"zsxmMc":kk_item_name,"msg":""}
        # print('kk_post_data',kk_post_data)

        kk_ret = htool.post_data(self.tax_kk_submit_url,parse,self.driver)
        if kk_ret.status_code == 200:
            kk_json = json.loads(kk_ret.text)
            print('扣款结果',kk_json)
            self.driver.execute_script("window.location.reload()")
            if kk_json['code'] == 200:
                # 扣款成功,继续扣款
                kk_post_data['msg'] = kk_item_name+',扣款成功'
                kk_post_data['kk_status'] = 1
                self.insert_log(kk_item_name+',扣款成功')
                # 延迟一下，否则可能扣款失败
                sleep(3)
                self.do_tax_kk_action(bank_num)
            else:
                # 多个账户时可以轮流扣款
                # self.driver.execute_script("layer.closeAll();")
                if bank_num > 1:
                    bank_num -= 1
                    print('扣除其它账户',kk_json)
                    return self.do_tax_kk_action(bank_num)
                else:
                    err_msg = '扣款失败，['+kk_item_name+'] '+kk_json['error']['errorMsgs'][0]
                    kk_post_data['msg'] = err_msg
                    self.insert_log(err_msg)
        else:            
            err_msg = kk_item_name+',提交扣款信息失败'
            self.insert_log(err_msg)
            kk_post_data['msg'] = err_msg
        print('客户端返回的扣款结果',kk_post_data)    
        return kk_post_data

    # 重新更新缴款信息
    def update_kk_info(self,jkrqq = '',jkrqz = ''):
        htool = HTool()
        if jkrqq == '':
            jkrqq = self.sbrqq
        if jkrqz == '':
            jkrqz = self.sbrqz

        data = {'jkrqq': jkrqq,'jkrqz': jkrqz,'ssqq': '','ssqz':'','uuid':self.fuser['uuid']}
        ret_msg = '获取申报统计数据失败'
        self.insert_log('更新扣款状态%s - %s' % (jkrqq,jkrqz))
        try:
            kk_data = htool.post_data(self.kk_update_url,data,self.driver)
        except Exception as e:
            # 这里需要重新添加任务
            print('重新更新结果时发生错误',e)
            return ret_msg
        print('扣款税务端返回汇总结果',kk_data.text)
        if kk_data and kk_data.status_code == 200:
            post_data = {}
            # 通用代码，执行到此步，默认通用项目已经扣除
            try:
                tax_json = json.loads(kk_data.text)
                parse_data = tax_json['data'][0]
                kk_data = self.kk_gl(parse_data,jkrqq,jkrqz)
                
                ret_msg = ''
                for kk in kk_data:
                    xmdm = ['BDA0610100']
                    parse_data = kk_data[kk]

                    for it in parse_data:
                        if 'YZPZZL_DM' in it:
                            print('税种代码',it['YZPZZL_DM'])
                            if it['YZPZZL_DM'] != '':
                                xmdm.append(it['YZPZZL_DM'])
                            if 'TFRQ' in it:
                                jkrqq = jkrqz = it['TFRQ']
                            elif 'SJRQ_1' in it:
                                jkrqq = jkrqz = it['SJRQ_1']
                    post_data['corpid'] = self.corpid
                    post_data['jkrqq'] = jkrqq
                    post_data['jkrqz'] = jkrqz
                    post_data['tbrq'] = jkrqz
                    post_data['json_data'] = json.dumps(list(set(xmdm)))
                    # print(jkrqq)
                    post_data['msg'] = '更新扣款状态 [缴款日期：%s] 成功' % jkrqq
                    print('扣款更新信息',post_data)
                    update_res = htool.post_data(self.bundle_kk_status_url,post_data)
                    print('扣款更新信息结果',update_res.text)
                    if update_res.status_code == 200:
                        kk_json = json.loads(update_res.text)
                        err = kk_json['text']
                        ret_msg += err
                    else:
                        err = '上传扣款数据时发生错误'
                        ret_msg += err
                    self.insert_log(err)    
                return ret_msg
            except Exception as e:
                ret_msg = '获取待扣款数据失败，请检查'
                print(e)
                # self.taxObj.remove_task()
                return ret_msg

    # 税收数据归类
    def kk_gl(self,kk_data,jkrqq,jkrqz):
        # print(sl_data)
        gl_dict = {}
        htool = HTool()
        ran_month = htool.get_month_range(jkrqq,jkrqz)
        for t_period in ran_month:
            gl_dict[t_period] = [{"TFRQ":t_period,"YZPZZL_DM":""}]
        for d in kk_data:
            for ss in kk_data[d]:
                if 'TFRQ' in ss:
                    fill_date_arr = ss['TFRQ'].split('-')
                elif 'SJRQ_1' in ss:
                    fill_date_arr = ss['SJRQ_1'].split('-')
                fill_date = "%s-%s-01" % (fill_date_arr[0],fill_date_arr[1])
                if fill_date in gl_dict:
                    gl_dict[fill_date].append(ss)
                else:
                    gl_dict[fill_date] = [ss]

        return gl_dict

    # 获取未扣款数据
    def get_kk_data(self):
        htool = HTool()
        post_res = htool.get_data(self.tax_kk_info_url)
        if post_res.status_code == 200:
            return json.loads(post_res.text)
        else:
            return {}

    # 信诺网代开发票查询
    def xnw_dkfp_search(self):
        pass 

    # 代开发票查询
    def sw_dkfp_search(self):
        htool = HTool()
        # kjrq = time.strftime("%Y-%m-01",time.localtime())

        kjrqq,kjrqz = htool.month_get(1)
        data = {'kjrqq': kjrqq,'kjrqz': kjrqz}
        ret_msg = '获取代开发票数据失败'
        # try:
        # 发票开具信息查询
        self.taxObj.remove_task()
        dkfp_ret = htool.post_data(self.dkfp_data_url,data,self.driver)
        print('代开发票日期参数',data)   
        if dkfp_ret.status_code == 200:
            dkfp_data = json.loads(dkfp_ret.text)
            print('代开票开具数据',dkfp_data)
            kj_ret = htool.post_data(self.agent_invoice_url,{"corpid":self.corpid,"msg":"已开具发票信息，共获取 %s 条" % len(dkfp_data['data']),"rows_data":json.dumps(dkfp_data['data'])})
            print("代开发票上传",kj_ret.text)
            fp_detail = self.dkfp_detail(1)
            # print(fp_detail)
            post_fp = htool.post_data(self.agent_invoice_detail_url,{"corpid":self.corpid,"msg":"发票办理信息,共获取： %s 条" % len(fp_detail),"rows_data":json.dumps(fp_detail)})
            print("发票详情上传",json.dumps(fp_detail))
            # except:
            #     return ret_msg
        else:
            print(ret_msg)

    def dkfp_detail(self,pageNum):
        # 发票申请
        data = {'pageSize': '2000','pageNum': pageNum,'formType':'A02'}
        # ret_msg = '获取代开发票申请数据失败'
        htool = HTool()
        # try:
        dkfp_data = htool.post_data(self.dkfp_detail_url,data,self.driver)
        # print('获取到发票申请信息',dkfp_data.text)
        if dkfp_data.status_code == 200:
            dkfp_json = json.loads(dkfp_data.text)
            # print(dkfp_json)
            if float(dkfp_json['data']['total']) > 0 and len(dkfp_json['data']['rows']) > 0:
                ret_json = []
                for dk in dkfp_json['data']['rows']:
                    app_time_arr = dk['createtime'].split('-')
                    if int(app_time_arr[0]) < 2020:
                        continue
                    # 过滤部分异常状态数据
                    if dk['stacode'] == '18' or dk['stacode'] == '3':
                        continue

                    d_link = self.zzfp_detail_url + dk['data_ID']
                    get_agent = htool.get_data(d_link,self.driver)
                    tax_node = BeautifulSoup(get_agent.text,'html.parser')
                    input_obj = tax_node.select('input[type="text"]')
                    row_detail = {"data_id":dk['data_ID'],"apply_time":dk['createtime'],"item_name":dk['table_NAME'],"ywlsh":dk['ywlsh']}
                    for input in input_obj:
                        # print(input['name'])
                        # if 'name' in input:
                        #     print(input['name'])
                        k_name = input.get('name')
                        if k_name != None:
                            if k_name not in ['hwlwmc','ggxh','hlsl','dj','je','jsxj','kce','slzsl','se','jylb']:
                                row_detail[k_name] = input.get("value")
                    
                    tr_pro = tax_node.find(id='tableTest').find('tbody').find_all('tr')
                    pro_list = []
                    for pro_row in tr_pro:
                        pro_detail = {}
                        pro_one = pro_row.select('input[type="text"]')
                        for p_parse in pro_one:
                            p_name = p_parse.get('name')
                            if p_name:
                                pro_detail[p_name] = p_parse.get('value')
                        pro_list.append(pro_detail)        
                    row_detail['pro'] = pro_list           
                    ret_json.append(row_detail)
                    # print(pro_list)
                return ret_json
            else:
                return []
        # except:
        #     print('解析错误')
        #     return ret_msg

    # 税费（种）认定信息 
    def ready_tax_info(self):
        rt_dict = []
        tax_dict = {}
        already_tax = []
        htool = HTool()
        sb_status = 0
        # try:
        tax_info = htool.get_data(self.tax_info_url,self.driver)
        self.sbrqq = time.strftime("%Y-%m-01",time.localtime())
        self.sbrqz = time.strftime("%Y-%m-%d",time.localtime())
        data = {'sbrqq': self.sbrqq,'sbrqz': self.sbrqz,'zsxmDm': '','uuid':self.fuser['uuid']}
        try:
            sb_data = htool.post_data(self.tax_data_url,data,self.driver)
        except Exception as e:
            print(e)
            return sb_status,tax_dict

        htool = HTool()
        # print('获取已申报数据',sb_data.text)

        if sb_data and sb_data.status_code == 200:
            try:
                tax_json = json.loads(sb_data.text)
                tax_data = tax_json['data']
                for tax_it in tax_data:
                    already_tax.append(tax_it['BDDM']+':'+tax_it['SKSSQQ'])
            except:
                print('解析已申报数据出错')
                return sb_status,tax_dict
        else:
            print('获取已申报数据失败')
            return sb_status,tax_dict 
        if tax_info:
            tax_node = BeautifulSoup(tax_info.text,'lxml')
            tax_array = tax_node.find(id='tableTest2').find('tbody').find_all('tr')
            
            aj_dict = ['01','04','07','10']
            for node in tax_array:
                td_arr = node.get_text().strip('\n')
                rt_dict.append(td_arr.split('\n'))
            for it in rt_dict:
                # 年报这里待修改
                if it[4] == '年':
                    ss_period = 12
                if it[4] == '季':
                    ss_period = 3
                if it[4] == '月':
                    ss_period = 1
                if it[4] == '次':
                    ss_period = 0
                ssqq,ssqz = htool.month_get(ss_period)
                # 首先过滤掉认定日期为本月的
                now_month = time.strftime("%Y-%m-01")
                mm = time.strftime("%m")
                if now_month == it[6] or it[1] != '自行申报':
                    continue
                
                if it[4] == '季':
                    if mm not in aj_dict:
                        continue
                # 年报的时间是1-6月
                if it[4] == '年':
                    pass
                if int(mm) > 6 and it[4] == '年':
                    continue

                tax_bd = json.loads(self.tax_config_info['ah_tax'])
                for cf in tax_bd:
                    if it[2] in cf['keyword'] and it[4] in cf['keyword']:
                        sz_bddm = cf['bddm']
                        if ((sz_bddm + it[4]) not in tax_dict) and (sz_bddm+":"+ssqq not in already_tax):
                            tax_dict[(sz_bddm + it[4])] = {"corpid":self.corpid,"bddm":sz_bddm,"ss_period":ss_period,"ssqq":ssqq,"ssqz":ssqz,"desc":cf['desc'],"tax_link":self.tax_config_info['ah_sb_url_pre'] + "bddm=%s&ssqq=%s&ssqz=%s" % (sz_bddm,ssqq,ssqz)}

        # except:
        #     print('读取解析税费种认定信息时发生错误')
        #     return False
        print('self.ready_tax',tax_dict)
        self.ready_tax = tax_dict
        return True


    # 获取未报税数据
    def get_tax_data(self):
        htool = HTool()
        post_res = htool.get_data(self.tax_report_info_url)
        if post_res.status_code == 200:
            return json.loads(post_res.text)
        else:
            return {}

    # 获取未上传代开具发票企业
    def get_dkjfp_data(self):
        htool = HTool()
        post_res = htool.get_data(self.agent_ready_url)
        if post_res.status_code == 200:
            return json.loads(post_res.text)
        else:
            return {}

    # 获取未上传社保缴纳信息企业
    def get_sb_jk_data(self):
        htool = HTool()
        post_res = htool.get_data(self.ready_sb_jk_detail_url)
        if post_res.status_code == 200:
            return json.loads(post_res.text)
        else:
            return {}

    # 获取需要上传报税数据企业
    def get_sw_sb_data(self):
        htool = HTool()
        post_res = htool.get_data(self.ready_sw_url)
        if post_res.status_code == 200:
            return json.loads(post_res.text)
        else:
            return {"rows":[]}

    # 社保申报
    def social_insurance(self):
        self.taxObj.remove_task()
        post_data = {"corpid":self.corpid,"content":"","comp_status":0}
        htool = HTool()
        ssqz = htool.last_day_of_month()
        si_url = self.tax_config_info['ah_sb_url_pre'] + 'nsrsbh=%s&bddm=SBFSB01&uuid=&ssqq=%s&ssqz=%s' % (self.credit_code,time.strftime("%Y-%m-01",time.localtime()),ssqz)
        self.driver.get(si_url)
        sb_jn_ret = htool.driver_close_alert(self.driver,3)    
        # 判断有无社保或需不需要缴纳
        if len(sb_jn_ret) > 0:
            print(sb_jn_ret[-1])
            post_data['content'] = sb_jn_ret[-1]
            # 无需申报无需申报
            if '您尚未进行社保登记' in sb_jn_ret[-1]:
                post_data['comp_status'] = 9
                return self.check_sb_result(post_data)
            # 可能已经申报过 
            elif '没有查询到人社部门的核定信息' in sb_jn_ret[-1]:
                post_data['comp_status'] = 1
                return self.check_sb_result(post_data)
            else:
                return self.check_sb_result(post_data)

        # sb_account = 499096
        # sb_pwd = 499096
        # 登录社保网站核定金额
        sb_site = SbExport(self)
        login_ret = sb_site.login(post_data,self.corpid)
        if login_ret['ret'] == False:
            return self.check_sb_result(login_ret)
        # 检查社保局核定的金额 
        hd_je = sb_site.get_sb_data()
        print('核定社保金额',hd_je)
        self.driver.get(si_url)
        self.driver.execute_script("$('.sbt .sbt-checkbox').click();")
        self.iframe = self.driver.find_element_by_xpath('//iframe[@id = "childIframe"]')
        self.driver.switch_to.frame(self.iframe)

        # 金额对比
        hd_sb_data = self.driver.execute_script("return $('#sbfjs').table('getData');")
        print('税务核定数据',hd_sb_data)
        yjfe = 0
        for mx_item in hd_sb_data:
            yjfe += float(mx_item['yjfe'])
        if int(yjfe) != hd_je:
            post_data['comp_status'] = 2
            post_data['content'] = '税务网站与社保网站应缴金额不一致，请确定'
            return self.check_sb_result(post_data)
        self.driver.execute_script("$('#sbfjs .sbt-checkbox-all').click();")

        print('社保检验')
        # self.driver.switch_to.default_content()
        self.driver.execute_script("shenbao();")
        fjs_ret = htool.driver_close_alert(self.driver,3)    
        print(fjs_ret[-1])
        post_data['content'] = fjs_ret[-1]
        return self.check_sb_result(post_data)

    # 继续判断处理社保申报结果
    def check_sb_result(self,result):
        print('继续判断社保结果',result)
        htool = HTool()
        post_data = {"corpid":self.corpid,"content":"","sb_status":0}
        sb_ret = False
        if result['comp_status'] == 1:
            # 延迟几秒时间，避免未查询到数据问题
            sleep(3)
            sb_ret = self.get_sb_detail(False)
            # print('最终上传社保结果',sb_ret)
            if sb_ret == True:
                post_data['content'] = '社保已申报并上传成功'
                post_data['sb_status'] = 1
        elif result['comp_status'] == 9:
            post_data['sb_status'] = 9
            post_data['content'] = result['content']
        else:
            post_data['sb_status'] = 2
            post_data['content'] = result['content']     
            
        export_data = htool.post_data(self.sb_auto_ret_url,post_data)
        if export_data.status_code != 200:
            print('上传报税结果错误',export_data.text)
        else:
            self.insert_log('成功提交社保申报结果')
        # print('社保接口提交数据',post_data)


    def tax_si_upload(self,page=0,page_size = 20000,tax_data = []):
        # sbrqq = time.strftime("%Y%m",time.localtime())
        # sbrqz = time.strftime("%Y%m",time.localtime())
        print('社保数据获取',self.sbrqq,self.sbrqz)
        data = {'qsrq00': self.sbrqq,'jzrq00': self.sbrqz,'aac002': '','aac003':'','aae140':'','aae078':'','pageIndex':page,'pageSize':page_size}
        htool = HTool()
        try:
            sb_data = htool.post_data(self.sb_jk_list_url,data,self.driver)
            tax_json = json.loads(sb_data.text)
            if tax_json['data'] != None:
                # print('获取到数据',tax_json,len(tax_json['data']))
                tax_data.extend(tax_json['data'])
                if tax_json['total'] > page_size:
                    print('继续获取下一页数据')
                    return self.tax_si_upload(page+1,page_size,tax_data)
             
        except Exception as e:
            print(e)

        # print('获取结果',tax_json['data'])
        # 数据归类并上传
        if len(tax_data) > 0 and (tax_json['data'] == None or tax_json['total'] <= page_size):
        # if len(tax_data) > 0:
            self.sy_tax_si(tax_data)

    def sy_tax_si(self,tax_data):
        gl_data = {}
        htool = HTool()
        for it in tax_data:
            if it['aae002'] not in gl_data:
                gl_data[it['aae002']] = [it]
            else:
                gl_data[it['aae002']].append(it)
        # 数据继续归类，上传
        for gl in gl_data:
            rows = gl_data[gl]
            # 按照人汇总
            users = {}
            post_user = []
            kk_date = ''
            for sig in rows:
                user_sign = sig['aae003']+sig['aac002']
                if user_sign not in users:
                    kk_date = sig['aae002']
                    users[user_sign] = {"data_id":"%s%s" %(self.corpid,user_sign),"kk_date":sig['aae002'],"identify":sig['aac002'],"type":sig['aaa115'],"type_name":sig['aaa115_mc'],"period":sig['aae003'],"uname":sig['aac003'],"total_money":float(sig['aae022'])+float(sig['aae020']),"gr":float(sig['aae022']),"dw":float(sig['aae020'])}
                else:
                    users[user_sign]["gr"] += float(sig['aae022'])
                    users[user_sign]["dw"] += float(sig['aae020'])
                    users[user_sign]["total_money"] += float(sig['aae022']) + float(sig['aae020'])
            for po in users:
                staff = users[po]
                staff['gr'] = "%.2f" % staff['gr']
                staff['dw'] = "%.2f" % staff['dw']
                staff['total_money'] = "%.2f" % staff['total_money']
                post_user.append(staff)
            print('汇总数据',len(post_user))    
            sb_ret = htool.post_data(self.sb_jk_detail_upload_url,{"post_user":json.dumps(post_user),"corpid":self.corpid,"kk_date":kk_date})
            if sb_ret.status_code != 200:
                print("post_user",sb_ret.text)

    # 报税
    def tax_sb(self):
        hd_ret = self.ready_tax_info()
        htool = HTool()
        post_data = {"corpid":self.corpid,"content":"","tax_status":0}
        self.sbrqq = time.strftime("%Y-%m-01",time.localtime())
        self.sbrqz = time.strftime("%Y-%m-%d",time.localtime())
        # 报税完成状态
        tax_sb_status = False

        # 核定失败了
        if hd_ret == False:
            return False
        # print('核定申报',self.ready_tax)
        
        # try:
        # 印花税按次申报，全部零申报(需要先查询下税费核定)
        # self.yhs_ac_sb()
        if len(self.ready_tax) != 0:
            # 解析链接中绑定代码分批次报税
            log_arr = []
            for tax_name in self.ready_tax:
                tax = self.ready_tax[tax_name]
                self.insert_log(tax['desc'])
                # 先报增值税，再报附加税
                if tax['bddm'] == 'FJSF001':
                    continue
                sb_ret = self.do_tax_sb(tax)
                log_arr.append(sb_ret+'[%s]' % tax['desc'])

            # 延迟几秒再查询，否则数据更新不及时
            sleep(5)
            # 比对数据，上传结果
            hd_ret = self.ready_tax_info()

            # 待申报数据为空，继续上传报表为成功
            if hd_ret == True and len(self.ready_tax) == 0:
                tax_sb_status = True
            post_data['content'] = ','.join(log_arr)
        else:
            tax_sb_status = True
            print('待申报为空')

        print('报税完成状态',tax_sb_status)
        if tax_sb_status == True:
            # 报税完成，更新报税信息数据成功时修改报税状态
            print('获取报税信息结果')
            tax_sb = self.get_tax_detail()
            if tax_sb == True:
                if post_data['content'] == '':
                    post_data['content'] = '更新上传纳税申报信息成功'
                post_data['tax_status'] = 1
        print('汇总结果',post_data)        
        export_data = htool.post_data(self.sb_auto_ret_url,post_data,self.driver)
        if export_data.status_code != 200:
            print('上传报税结果错误')
        # except:
        #     ret_msg = '获取代办事项失败'
        #     return ret_msg

    def do_tax_sb(self,tax_info):
        bddm = tax_info["bddm"]
        tax_url = tax_info["tax_link"]
        ss_period = tax_info["ss_period"]
        htool = HTool()          

        # 打开网页，获取数据
        # 通用申报
        if bddm == 'TYSB100':
            self.driver.get(tax_url)
            htool.driver_close_alert(self.driver,3)
            parse_sb_data = self.driver.execute_script("return $('#sbbTable').table('getData');")

            st_index = 0
            for sb_item in parse_sb_data:
                # 水利建设基金
                if 'zspmDm' in sb_item and sb_item['zspmDm'] == '302210400':
                    # 报税所需数据
                    sb_data = self.get_tax_sb_data(tax_info)
                    if 'pmdm' not in sb_data or 'shouru' not in sb_data:
                        print('水利基金获取报税数据失败')
                        return False
                    print('申报数据',sb_data)
                    sr_total = sb_data['shouru']
                    self.driver.execute_script("$('input[name=ysx]').eq(%s).val(%s).trigger('change');" % (st_index,sr_total))
                    htool.driver_close_alert(self.driver)
                st_index += 1    
            self.driver.execute_script("shenbao();")
        # 企业所得税(暂未区分A类或B类)
        elif bddm == 'SDSYJB93':
            self.insert_log('企业所得税申报')
            self.driver.get(tax_url)
            htool.driver_close_alert(self.driver,3)
            # $('#page-tree').children('option').length
            # 本年收入累计
            sb_data = self.get_tax_sb_data(tax_info)
            if 'pmdm' not in sb_data or 'shouru' not in sb_data:
                print('企业所得税获取报税数据失败')
                return False

            # sb_data['shouru'] = 1452552.5
            # sb_data['estimate_qysds_money'] = 5855
            yysr = sb_data['shouru']

            # 填写附表部分
            option_num = self.driver.execute_script("return $('#page-tree').children('option').length;")
            for i in range(int(option_num)-1):
                # print(i+1)
                self.driver.execute_script("$(\"#page-tree option\").eq(%s).attr(\"selected\",true).trigger('change');" % (i+1))
                fname = self.driver.execute_script("return $(\"#page-tree option\").eq(%s).attr(\"name\");" % (i+1))
                self.driver.switch_to.default_content()
    
                # A203010居民企业参股外国企业信息报告表跳过
                if fname != 'A203010':
                    self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "%s"]' % fname)
                    self.driver.switch_to.frame(self.iframe)
                    self.driver.execute_script("$('#warp .sbt-btnList button').click();")
                    self.driver.switch_to.default_content()
                sleep(3)
            # 填写主表部分
            self.driver.switch_to.default_content()
            self.driver.execute_script("$(\"#page-tree option\").attr(\"selected\",false).trigger('change');")
            main_name = self.driver.execute_script("return $(\"#page-tree option\").eq(0).attr(\"name\");")
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "%s"]' % main_name)
            self.driver.switch_to.frame(self.iframe)
            # 实际已缴纳所得税额
            
            # # 13行实际已缴纳所得税额
            # yjsdse = self.driver.execute_script("return $('#sbbxxForm input[name=sjyyjsdseLj]').val();")
            # # 14行 特定业务预缴（征）所得税额
            # tdywyjzsdseLj = self.driver.execute_script("return $('#sbbxxForm input[name=tdywyjzsdseLj]').val();")
            # # 15行 符合条件的小型微利企业延缓缴纳所得税额
            # fhtjxwqyyhjzsdseLj = self.driver.execute_script("return $('#sbbxxForm input[name=fhtjxwqyyhjzsdseLj]').val();")

            if float(yysr) > 0:

                #1 营业收入
                self.driver.execute_script("$('#sbbxxForm input[name=yysrLj]').val(%s).trigger('change');" % yysr)
                # 客户交税，填写客户交税部分利润，不交税控制利润-2000~-5000
                if float(sb_data['estimate_qysds_money']) > 0:
                    # 客户交税
                    lr_total = sb_data['estimate_qysds_money']
                else:
                    # 客户不交税
                    lr_total = random.randint(-5000,-2000)

                #3 利润总额    
                self.driver.execute_script("$('#sbbxxForm input[name=lrzeLj]').val(%s).trigger('change');" % round(lr_total,2))

                #2 营业成本
                self.driver.execute_script("$('#sbbxxForm input[name=yycbLj]').val(%s).trigger('change');" % round((float(yysr) - lr_total),2))

            # 是否高新技术企业 科技型中小企业 技术入股递延纳税事项
            self.driver.execute_script("$('input[name=sfgxjsqy][value=\"N\"]').prop('checked',true);$('input[name=sfkjxzxqy][value=\"N\"]').prop('checked',true);$('input[name=sffsjsrgdynssx][value=\"N\"]').prop('checked',true);")
            # 从业人数
            mm = time.strftime("%m")
            jc_rs = jm_rs = jc_ze = jm_ze = 1
            lart_j = 0
            if int(mm) > 6:
                lart_j = math.ceil((int(mm)-1)/3) - 1
                jc_rs = self.driver.execute_script("return $('#seasonForm input[name=qccyrs%s]').val();" % lart_j)
                jm_rs = self.driver.execute_script("return $('#seasonForm input[name=qmcyrs%s]').val();" % lart_j)
                jc_ze = self.driver.execute_script("return $('#seasonForm input[name=qczcze%s]').val();" % lart_j)
                jm_ze = self.driver.execute_script("return $('#seasonForm input[name=qmzcze%s]').val();" % lart_j)

            now_j = lart_j + 1
            self.driver.execute_script("$('#seasonForm input[name=qccyrs%s]').val(%s);" % (now_j,jc_rs))
            self.driver.execute_script("$('#seasonForm input[name=qmcyrs%s]').val(%s);" % (now_j,jm_rs))
            self.driver.execute_script("$('#seasonForm input[name=qczcze%s]').val(%s);" % (now_j,jc_ze))
            self.driver.execute_script("$('#seasonForm input[name=qmzcze%s]').val(%s);" % (now_j,jm_ze))
            self.driver.switch_to.default_content()
            self.driver.execute_script("shenbao();")

        # # 附加税
        # elif bddm == 'FJSF001':
        #     self.insert_log('附加税申报')
        #     self.driver.get(tax_url)
        #     # parse_sb_data = self.driver.execute_script("return $('#mxTable').table('getData');")
        #     htool.driver_close_alert(self.driver,3)
        #     # self.driver.execute_script("$('input[name=ybzzs]').val(2525).trigger('change');")
        #     # 测试数据，需要修改正确数据
        #     self.driver.execute_script('var iframe = $("#iframes", parent.document).find("iframe[name=main]")[0];var fc = iframe.contentWindow.document;$(fc).find(\'input[name=ybzzs]\').val("500.00");')
        #     self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "main"]')
        #     self.driver.switch_to.frame(self.iframe)
        #     # 触发iframe input修改操作
        #     for i in range(3):
        #         self.driver.find_element_by_xpath('//div[@id="mxTable"]//tbody/tr[%s]//input[@name="ybzzs"]' % (i+1)).send_keys('0')

        #     self.driver.switch_to.default_content()
        #     self.driver.execute_script("shenbao();")

        # 印花税
        elif bddm == 'YHS0794':
            # 印花税按次申报无需操作
            self.driver.get(tax_url)
            htool.driver_close_alert(self.driver,3)

            # 印花税按月申报 
            if ss_period == 3:
                # 征收品目代码
                self.driver.get(tax_url)
                htool.driver_close_alert(self.driver,3)
                parse_sb_data = self.driver.execute_script("return $('#mxTable').table('getData');")

                # 报税所需数据
                sb_data = self.get_tax_sb_data(tax_info)
                if 'pmdm' not in sb_data or 'shouru' not in sb_data:
                    print('印花税获取报税数据失败')
                    return False

                pmdm = sb_data['pmdm']
                sr_total = sb_data['shouru']

                # 是否能匹配上
                pm_match = False
                # 其它匹配项
                retry_index = 0
                p_index = 0
                for sb_item in parse_sb_data:
                    if sb_item['zspmDm'] == pmdm:
                        pm_match = True
                        self.driver.execute_script("$('.sbt input[name=jsje]').eq(%s).val(%s).trigger('change');" % (p_index,sr_total))
                    # 选择不是资金账簿的作为备选 
                    elif sb_item['zspmDm'] != "101110501":
                        retry_index = p_index
                    p_index += 1
                # 如果未匹配上选择其它匹配项
                if pm_match == False:
                    self.driver.execute_script("$('.sbt input[name=jsje]').eq(%s).val(%s).trigger('change');" % (retry_index,sr_total))
            self.driver.execute_script("shenbao();")  

        # 一般纳税人增值税 
        elif bddm == 'SB00112':
            print('增值税链接',tax_url)
            self.driver.get(tax_url)
            htool.driver_close_alert(self.driver,3)
            self.driver.execute_script("layer.closeAll();")
            # self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z01']\").attr(\"selected\",true).trigger('change');")
            # htool.driver_close_alert(self.driver,3)
            # sleep(3)
            # 报税所需数据
            sb_data = self.get_tax_sb_data(tax_info)
            if len(sb_data) == 0:
                print('无报税数据')
                return False
            # 测试数据
            # sb_data['sr_sk_z'] = sb_data['sr_13_lw_z'] = '16460.17'
            # sb_data['tax_13_lw_z'] = '2139.83'
            # # 进项税额
            # sb_data['jx_se'] = '8681.25'

            sleep(1)
            # 填写附表2
            self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z02']\").attr(\"selected\",true).trigger('change');")
            msg_dic = htool.driver_close_alert(self.driver,3)
            print('弹框消息',msg_dic)
            # 税控盘未抄税情况
            for ms_it in msg_dic:
                if '完成汇总报送' in ms_it:
                    return False

            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z02"]')
            self.driver.switch_to.frame(self.iframe)
            sleep(1)

            # 8b火车票机票等
            print('8b火车票机票等')
            if float(sb_data['hcp_fjp_number']) > 0 and float(sb_data['hcp_fjp_net_income']) > 0:
                self.driver.execute_script("$('#bqjxsemxbForm input[name=fs_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_number'])
                self.driver.execute_script("$('#bqjxsemxbForm input[name=je_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_net_income'])
                self.driver.execute_script("$('#bqjxsemxbForm input[name=se_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_tax_amount'])

                # 本期用于抵扣的旅客运输服务扣税凭证
                print('本期用于抵扣的旅客运输服务扣税凭证')
                self.driver.execute_script("$('#bqjxsemxbForm input[name=fs_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_number'])
                self.driver.execute_script("$('#bqjxsemxbForm input[name=je_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_net_income'])
                self.driver.execute_script("$('#bqjxsemxbForm input[name=se_8]').val(%s).trigger('change');" % sb_data['hcp_fjp_tax_amount'])

            # 红字专用发票信息表注明的进项税额
            if float(sb_data['red_rush_tax']) > 0:
                self.driver.execute_script("$('#bqjxsemxbForm input[name=se_20]').val(0).trigger('change');")
            self.driver.execute_script("getZ02Data();")

            sleep(1)
            # 填写附表4
            self.driver.switch_to.default_content()
            self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z04']\").attr(\"selected\",true).trigger('change');")
            htool.driver_close_alert(self.driver,3)
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z04"]')
            self.driver.switch_to.frame(self.iframe)
            # 增值税税控系统专用设备费及技术维护费
            if float(sb_data['skp_or_fwf_total']) > 0:
                self.driver.execute_script("$('#sedjqkbForm input[name=bqfse_zzsskxtfy_2]').val(%s).trigger('change');" % sb_data['skp_or_fwf_total'])
                # self.driver.execute_script("$('#sedjqkbForm input[name=bqsjdjse_zzsskxtfy_4]').val(%s).trigger('change');" % sb_data['skp_or_fwf_total'])
            # 外地预缴
            self.driver.execute_script("$('#sedjqkbForm input[name=bqfse_jzfwyzjnsk_2]').val(0).trigger('change');")
            self.driver.execute_script("$('#sedjqkbForm input[name=bqsjdjse_jzfwyzjnsk_4]').val(0).trigger('change');")
            self.driver.execute_script("getZ04Data();")

            sleep(1)
            # 填写增值税减免申报明细表
            self.driver.switch_to.default_content()
            self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z05']\").attr(\"selected\",true).trigger('change');")
            htool.driver_close_alert(self.driver,3)
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z05"]')
            self.driver.switch_to.frame(self.iframe)
            # 税控盘抵扣优惠情况
            if float(sb_data['skp_or_fwf_total']) > 0:
                self.driver.execute_script("$('#zzsjmssbmxbjsxmGrid .sbt-table-add').click();")
                sleep(1)
                # trigger可能报错，需要屏蔽
                try:
                    self.driver.execute_script("$('.sbt select[name=hmc]').find(\"option:contains('0001129917|SXA031900185')\").attr(\"selected\",true).trigger('change');")
                except:
                    pass  
                self.driver.execute_script("$('.sbt input[name=bqfse]').val(%s).trigger('change');" % sb_data['skp_or_fwf_total'])
                # self.driver.execute_script("$('.sbt input[name=bqsjdjse]').val(200).trigger('change');")
            self.driver.execute_script("getZ05Data();")
            self.driver.switch_to.default_content()
            # 免税收入暂时无法完成 pass

            sleep(1)
            # 填写附表1
            self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z01']\").attr(\"selected\",true).trigger('change');")
            htool.driver_close_alert(self.driver,3)
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z01"]')
            self.driver.switch_to.frame(self.iframe)

            tax_data = {"1":htool.to_match_f1(sb_data,'_lw','13'),"2":htool.to_match_f1(sb_data,'_fw','13'),"3":htool.to_match_f1(sb_data,'_lw','9'),"4":htool.to_match_f1(sb_data,'_fw','9'),"5":htool.to_match_f1(sb_data,'','6'),"11":htool.to_match_f1(sb_data,'_lw','3'),"12":htool.to_match_f1(sb_data,'_fw','3'),}

            for i in tax_data:
                z_x = self.driver.execute_script("return $('#bqxsqkmxbForm input[name=kjskzzszyfp_xse_1_%s]').val();" % i)
                z_e = self.driver.execute_script("return $('#bqxsqkmxbForm input[name=kjskzzszyfp_xxynse_2_%s]').val();" % i)
                p_x = self.driver.execute_script("return $('#bqxsqkmxbForm input[name=kjqtfp_xse_3_%s]').val();" % i)
                p_e = self.driver.execute_script("return $('#bqxsqkmxbForm input[name=kjqtfp_xxynse_4_%s]').val();" % i)

                if htool.match_fl_val(tax_data[i][0],z_x) == False or htool.match_fl_val(tax_data[i][1],z_e) == False or htool.match_fl_val(tax_data[i][2],p_x) == False or htool.match_fl_val(tax_data[i][3],p_e) == False:
                    # 数据匹配检验不对
                    print(i,tax_data[i][0],z_x,tax_data[i][1],z_e,tax_data[i][2],p_x,tax_data[i][3],p_e)
                    print('填写附表1时，数据不匹配，请人工检查后重新申报')
                    return False
            self.driver.execute_script("getZ01Data();")
            self.driver.switch_to.default_content()
            # sleep(250)
            # self.driver.execute_script("$('#bqxsqkmxbForm input[name=bqsjdjse]').val(200).trigger('change');")

            sleep(1)
            # 主表填写
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z00"]')
            self.driver.switch_to.frame(self.iframe)
            # 进项税额转出(红冲发票税额)
            if float(sb_data['red_rush_tax']) > 0:
                self.driver.execute_script("$('#sbbxxForm input[name=ybhwjlw_bys_14]').val(%s).trigger('change');" % sb_data['red_rush_tax'])
            # # ①分次预缴税额	(外地预缴实际抵减)
            self.driver.execute_script("$('#sbbxxForm input[name=ybhwjlw_bys_28]').val(0).trigger('change');")
            # 应纳税额减征额(税控盘与服务实际抵扣额)
            if float(sb_data['skp_or_fwf_total']) > 0:
                self.driver.execute_script("$('#sbbxxForm input[name=ybhwjlw_bys_23]').val(%s).trigger('change');" % sb_data['skp_or_fwf_total'])

            # 14行，进项税额
            if float(sb_data['jx_se']) > 0:
                self.driver.execute_script("$('#sbbxxForm input[name=ybhwjlw_bys_12]').val(%s).trigger('change');" % sb_data['jx_se'])

            rt_hj_1 = self.driver.execute_script("return $('#sbbxxForm input[name=ybhwjlw_bys_24]').val();")
            rt_hj_2 = self.driver.execute_script("return $('#sbbxxForm input[name=ybhwjlw_bnlj_24]').val();")
            yn_hj = float(rt_hj_1.replace(',','')) + float(rt_hj_2.replace(',',''))
            print('应纳税额合计',yn_hj)
            self.driver.switch_to.default_content()
            sleep(1)

            # 填写附表3
            # 填写6%价税合计
            ys_fw_kc = float(sb_data['sr_6_z']) + float(sb_data['tax_6_z']) + float(sb_data['sr_6_p']) + float(sb_data['tax_6_p'])
            if ys_fw_kc > 0:
                self.driver.execute_script("$(\"#page-tree\").find(\"option[name='Z03']\").attr(\"selected\",true).trigger('change');")
                htool.driver_close_alert(self.driver,3)
                self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "Z03"]')
                self.driver.switch_to.frame(self.iframe)
                self.driver.execute_script("$('#ysfwkcxmmxForm input[name=bqysfwjghjemsxse_1_6]').val(%s).trigger('change');" % ys_fw_kc)
                self.driver.execute_script("getZ03Data();")
                sleep(1)
                self.driver.switch_to.default_content()
            self.driver.execute_script("shenbao();")
            sb_ret =  htool.driver_close_alert(self.driver,4)
            print('一般纳税人增值税报税结果',sb_ret[-1])
            
            # 附加税申报
            fjs_url = tax_url.replace('SB00112','FJSF001')
            self.driver.get(fjs_url)
            htool.driver_close_alert(self.driver,4)
            self.driver.execute_script("layer.closeAll();")
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "main"]')
            self.driver.switch_to.frame(self.iframe)
            # 应纳税额大于0的情况下，才需要填表
            if yn_hj > 0:
                self.driver.execute_script("$('#mxTable input[name=ybzzs]').val(%s).trigger('change');" % yn_hj)
                # 后面替换成后台传递的数值
                cj_yj = 0
                jy_yj = 0
                df_yj = 0

                fs_data = self.driver.execute_script("return $('#mxTable').table('getData');")
                it_st = 0
                for fs_it in fs_data:
                    # 地方教育附加
                    if fs_it['zspmDm'] == '101090101':
                        if cj_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(cj_yj,2)))
                    # 城市维护建设税 
                    elif fs_it['zspmDm'] == '302030100':
                        if jy_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(jy_yj,2)))
                    # 教育费附加        
                    elif fs_it['zspmDm'] == '302160100':
                        if df_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(df_yj,2)))

                    it_st += 1
            self.driver.switch_to.default_content()
            self.driver.execute_script("shenbao();") 

        # 小规模增值税
        elif bddm == 'SB00212':
            # 代开发票数据
            dk_data = self.dkfp_bs_search(tax_info['ssqq'],tax_info['ssqz'])
            # 报税所需数据
            sb_data = self.get_tax_sb_data(tax_info)
            if len(sb_data) == 0:
                print('无报税数据')
                return False
            self.driver.get(tax_url)
            htool.driver_close_alert(self.driver,3)
            self.driver.execute_script("layer.closeAll();")
            
            # 切换到主表iframe
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "zzsxgmsb"]')
            self.driver.switch_to.frame(self.iframe)

            # 测试数据
            # sb_data['sr_sk_z'] = 1571539.54
            # sb_data['sr_3_fw_z'] = 1373519.74
            # sb_data['sr_1_fw_z'] = 198019.8

            # sb_data['skp_or_fwf_total'] = 200
            # sb_data['sr_1_lw_z'] = 80000
            # sb_data['sr_sk_p'] = sb_data['sr_1_fw_p'] = 97245.55
            # sb_data['skp_or_fwf_total'] = 200
            # 收入合计
            total_money = float(sb_data['sr_sk_p']) + float(sb_data['sr_dk']) + float(sb_data['sr_drxnw']) + float(sb_data['sr_tyjd']) + float(sb_data['sr_sk_z']) + float(sb_data['sr_wkp']) + float(sb_data['sr_xnw']) + float(sb_data['sr_qt']) - float(sb_data['red_rush_tax'])
            bqybt = 0

            lw_z_total = float(sb_data['sr_3_lw_z']) + float(sb_data['sr_1_lw_z'])
            lw_p_total = float(sb_data['sr_3_lw_p']) + float(sb_data['sr_1_lw_p'])
            fw_z_total = float(sb_data['sr_3_fw_z']) + float(sb_data['sr_1_fw_z'])
            fw_p_total =  float(sb_data['sr_3_fw_p']) + float(sb_data['sr_1_fw_p'])

            self.driver.execute_script("$('#sbbxxForm input[name=swjgdkdzzszyfpbhsxse_2_1]').val(%s).trigger('change');" % lw_z_total)
            self.driver.execute_script("$('#sbbxxForm input[name=swjgdkdzzszyfpbhsxse_2_2]').val(%s).trigger('change');" % fw_z_total)
            # 判断有没有开一个点的
            jm_item = float(sb_data['sr_1_lw_z']) + float(sb_data['sr_1_lw_p']) + float(sb_data['sr_1_fw_z']) + float(sb_data['sr_1_fw_p'])
            # 月收入超10w,季收入超30w
            if (total_money/ss_period) > 100000:
                # 货物及劳务
                lw_total = lw_z_total + lw_p_total
                fw_total = fw_z_total + fw_p_total
                self.driver.execute_script("$('#sbbxxForm input[name=yzzzsbhsxse_1_1]').val(%s).trigger('change');" % lw_total)
                self.driver.execute_script("$('#sbbxxForm input[name=yzzzsbhsxse_1_2]').val(%s).trigger('change');" % fw_total)
                self.driver.execute_script("$('#sbbxxForm input[name=skqjkjdptfpbhsxse_3_1]').val(%s).trigger('change');" % lw_p_total)
                self.driver.execute_script("$('#sbbxxForm input[name=skqjkjdptfpbhsxse_3_2]').val(%s).trigger('change');" % fw_p_total)
            else:
                # 货物及劳务
                self.driver.execute_script("$('#sbbxxForm input[name=xwqymsxse_10_1]').val(%s).trigger('change');" % lw_p_total)
                # 服务、不动产和无形资产
                self.driver.execute_script("$('#sbbxxForm input[name=xwqymsxse_10_2]').val(%s).trigger('change');" % fw_p_total)
                if jm_item > 0:
                    # 本期应纳税额减征额
                    self.driver.execute_script("$('#sbbxxForm input[name=bqmse_19_2]').val(%s).trigger('change');" % round(jm_item*0.03,2))
                    self.driver.execute_script("$('#sbbxxForm input[name=xwqymse_20_2]').val(%s).trigger('change');" % round(jm_item*0.03,2))

            # 应纳税额合计
            # $('#sbbxxForm input[name=ynsehj_22_2]').val()
            rt_hj_1 = self.driver.execute_script("return $('#sbbxxForm input[name=bqybtse_24_1]').val();")
            rt_hj_2 = self.driver.execute_script("return $('#sbbxxForm input[name=bqybtse_24_2]').val();")
            bqybt = float(rt_hj_1.replace(',','')) + float(rt_hj_2.replace(',',''))
           
            # 填写附表3
            self.driver.switch_to.default_content()
            self.driver.execute_script("$(\"#page-tree\").find(\"option[name='zzsjmssbmxb']\").attr(\"selected\",true).trigger('change');")
            htool.driver_close_alert(self.driver,3)
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "zzsjmssbmxb"]')
            self.driver.switch_to.frame(self.iframe)

            # 填写具体优惠
            yh_index = 0
            if (total_money/ss_period) > 100000 and jm_item > 0:
                # 新冠优惠期间1%点的优惠
                self.driver.execute_script("$('#zzsjmssbmxbTable .sbt-table-add').click();")
                # 选择框可能报错，需要屏蔽
                try:
                    self.driver.execute_script("$('.sb_table_select select[name=hmc]').eq(%s).find(\"option:contains('0001011608|SXA031901121')\").attr(\"selected\",true).trigger('change');" % yh_index)
                except:
                    pass
                self.driver.execute_script("$('#zzsjmssbmxbTable input[name=bqfse]').eq(%s).val(%s).trigger('change');" % (yh_index,round(jm_item*0.02,2)))
                self.driver.execute_script("$('#zzsjmssbmxbTable input[name=bqsjdjse]').eq(%s).val(%s).trigger('change');" % (yh_index,round(jm_item*0.02,2)))
                yh_index += 1
            # 税控盘实际抵减额
            sk_rel_dis = 0
            if float(sb_data['skp_or_fwf_total']) > 0:
                self.driver.execute_script("$('#zzsjmssbmxbTable .sbt-table-add').click();")
                # 选择框可能报错，需要屏蔽
                try:
                    self.driver.execute_script("$('.sb_table_select select[name=hmc]').eq(%s).find(\"option:contains('0001129914|SXA031900185')\").attr(\"selected\",true).trigger('change');" % yh_index)
                except:
                    pass
                self.driver.execute_script("$('#zzsjmssbmxbTable input[name=bqfse]').eq(%s).val(%s).trigger('change');" % (yh_index,sb_data['skp_or_fwf_total']))
                if bqybt > 0:
                    # 实际可抵扣金额
                    if bqybt > float(sb_data['skp_or_fwf_total']):
                        sk_rel_dis = float(sb_data['skp_or_fwf_total'])
                    else:
                        sk_rel_dis = bqybt
                    self.driver.execute_script("$('#zzsjmssbmxbTable input[name=bqsjdjse]').eq(%s).val(%s).trigger('change');" % (yh_index,sk_rel_dis))

            self.driver.execute_script("getJmForm();")
            jm_ret = htool.driver_close_alert(self.driver,3)
            if '校验通过' in jm_ret[-1]:
                print(jm_ret[-1])
            else:
                # 其它情况，待处理
                pass

            # 切换到主表iframe
            self.driver.switch_to.default_content()
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "zzsxgmsb"]')
            self.driver.switch_to.frame(self.iframe)
            # 重新填写实际可抵扣金额
            if sk_rel_dis > 0:
                self.driver.execute_script("$('#sbbxxForm input[name=bqynsejze_18_2]').val(%s).trigger('change');" % sk_rel_dis)
            # 本期应纳税额减征额 18-1 18-2
            if (total_money/ss_period) > 100000 and jm_item > 0:
                jm_lw_item = float(sb_data['sr_1_lw_z']) + float(sb_data['sr_1_lw_p'])
                self.driver.execute_script("$('#sbbxxForm input[name=bqynsejze_18_1]').val(%s).trigger('change');" % round(jm_lw_item*0.02,2))
                jm_fw_item = float(sb_data['sr_1_fw_z']) + float(sb_data['sr_1_fw_p']) + sk_rel_dis
                self.driver.execute_script("$('#sbbxxForm input[name=bqynsejze_18_2]').val(%s).trigger('change');" % round(jm_fw_item*0.02,2))
             
            rt_hj_1 = self.driver.execute_script("return $('#sbbxxForm input[name=ynsehj_22_1]').val();")
            rt_hj_2 = self.driver.execute_script("return $('#sbbxxForm input[name=ynsehj_22_2]').val();")
            yn_hj = float(rt_hj_1.replace(',','')) + float(rt_hj_2.replace(',',''))
            print('应纳税额合计',yn_hj)
            self.driver.switch_to.default_content()
            self.driver.execute_script("xgmshenbao();")
            sb_ret =  htool.driver_close_alert(self.driver,4)
            print('小规模增值税报税结果',sb_ret[-1])
            
            # 附加税申报
            fjs_url = tax_url.replace('SB00212','FJSF001')
            self.driver.get(fjs_url)
            htool.driver_close_alert(self.driver,4)
            self.driver.execute_script("layer.closeAll();")
            self.iframe = self.driver.find_element_by_xpath('//div[@id="iframes"]/iframe[@name = "main"]')
            self.driver.switch_to.frame(self.iframe)
            # 应纳税额大于0的情况下，才需要填表
            if yn_hj > 0:
                self.driver.execute_script("$('#mxTable input[name=ybzzs]').val(%s).trigger('change');" % yn_hj)
                # 后面替换成后台传递的数值
                cj_yj = 0
                jy_yj = 0
                df_yj = 0
                if '10109' in dk_data:
                    cj_yj += dk_data['10109']
                fs_data = self.driver.execute_script("return $('#mxTable').table('getData');")
                it_st = 0
                for fs_it in fs_data:
                    # 地方教育附加
                    if fs_it['zspmDm'] == '101090101':
                        if cj_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(cj_yj,2)))
                    if (total_money/ss_period) < 100000:
                        try:
                            self.driver.execute_script("$('#mxTable select[name=jmxzMc]').eq(%s).find(\"option:contains('%s')\").attr(\"selected\",true).trigger('change');" % (it_st,'0099129999|其他其他'))
                        except:
                            pass
                        htool.driver_close_alert(self.driver,1)
                    # 城市维护建设税 
                    if fs_it['zspmDm'] == '302030100':
                        if jy_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(jy_yj,2)))
                    # 教育费附加        
                    if fs_it['zspmDm'] == '302160100':
                        if df_yj > 0:
                            self.driver.execute_script("$('#mxTable input[name=bqyjse]').eq(%s).val(%s).trigger('change');" % (it_st,round(df_yj,2)))
                    if (total_money/ss_period) < 100000:
                        try:
                            self.driver.execute_script("$('#mxTable select[name=jmxzMc]').eq(%s).find(\"option:contains('%s')\").attr(\"selected\",true).trigger('change');" % (it_st,'0061042802|按月'))
                        except:
                            pass
                        htool.driver_close_alert(self.driver,1)
                    it_st += 1
            self.driver.switch_to.default_content()
            self.driver.execute_script("shenbao();")    
        else:
            print(bddm,'对应的报税方法正在完善')
        fjs_ret = htool.driver_close_alert(self.driver,3)    
        return fjs_ret[-1]

    # 获取报税所需的代开发票数据
    def dkfp_bs_search(self,ssqq,ssqz):
        data = {'kjms':'mxkj','skssqq': ssqq,'skssqz':ssqz,'rtkrqq':'','rtkrqz':'','kpsjq':'','kpsjz':'','sz':''}
        # ret_msg = '获取代开发票申请数据失败'
        # try:
        
        htool = HTool()
        dkfp_data = htool.post_data(self.agent_list_url,data,self.driver)
        dk_val = {}
        if dkfp_data.status_code == 200:
            tax_json = json.loads(dkfp_data.text)
            tax_data = tax_json['data']
            dk_val = {}
            for jj in tax_data:
                if jj['skssqz'][:7] != jj['skssqq'][:7]:
                    continue
                if jj['zsxmDm'] not in dk_val:
                    dk_val[jj['zsxmDm']] = float(jj['sjje'])
                else:
                    dk_val[jj['zsxmDm']] += float(jj['sjje'])
        print('查询代开发票数据',dk_val)            
        return dk_val

    # 获取报税所需数据   
    def get_tax_sb_data(self,post_data):
        htool = HTool()
        export_data = htool.post_data(self.tax_export_data_url,post_data,self.driver)
        if export_data.status_code == 200:
            try:
                # 对应税种所需报税数据
                parse_export = json.loads(export_data.text)
                return parse_export
            except:
                print("获取报税数据失败")
        return {}        

    def insert_log(self,text):
        self.taxObj.add_log(text)

        