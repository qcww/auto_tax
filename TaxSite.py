import requests
import json
import configparser
import sys
import os
import re
import ChToWod
import xml.dom.minidom
import logging
import time
from time import sleep
from urllib.parse import urlencode  #Python内置的HTTP请求库
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from HTool import HTool
from bs4 import BeautifulSoup
from xml.dom.minidom import parse

#税务局网站
class TaxSite:

    def __init__(self,lb,status_bar):
        base_dir=os.getcwd()
        sys.path.append(base_dir)

        htool = HTool()
        config = htool.rt_config()

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
        self.loggin_start()
        # 残疾人保障金申报信息获取地址
        self.new_tax_url = config['link']['new_tas_url']
        self.tax_update_url = config['link']['tax_update_url']
        self.sb_url = config['link']['sb_data_url']
        self.template = config['tax_template']
        self.run_status = {"receive_num":0,"success_num":0,"faild_num":0,"pass_err_num":0}
        self.run_status_name = {"receive_num":"接收","success_num":"成功","faild_num":"失败","pass_err_num":"密码错误"}
        
        self.lb = lb
        self.status_bar = status_bar
        
    def status_count(self,s_type,num = 1):
        self.run_status[s_type] += 1
        self.status_bar[s_type].set("%s：%s" % (self.run_status_name[s_type],self.run_status[s_type]))

    def set_corp(self,corp_list):
        self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action = corp_list.split('||',7)
        self.insert_log("收到请求:"+self.corpname + " " + self.action)
        # self.run_status['receive'] += 1
        # self.status_bar['receive_num'].set("已接收：%s" % self.run_status['receive'])
        self.status_count("receive_num")
        return self.corpid

    def loggin_start(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"                        # 日期格式
        fp = logging.FileHandler('error.txt', encoding='utf-8')
        fs = logging.StreamHandler()
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])    # 调用

    #打开浏览器
    def open_browser(self):
        self.driver = webdriver.Chrome()
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
        if login_times == 0:
            self.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'1','msg':'登录失败次数过多'})
            driver.quit()
            return False
        login_times -= 1
        
        try:
            #打开登录框
            Action = ActionChains(driver)# 实例化一个action对象
            login_open = driver.find_element_by_id("login")#获取打开登录框的按钮
            login_open_click = Action.click(login_open)#点击
            login_open_click.perform()
            sleep(3)

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
            sleep(5)
            # 判断是否有密码错误的提示框出来 
            pass_err = driver.find_element_by_id("layui-layer1")
            if pass_err:
                err_msg = driver.find_element_by_xpath("//div[@id='layui-layer1']/div[@class='layui-layer-content']").text
                if '您的密码已输错' in err_msg:
                    self.status_count("pass_err_num")
                    self.insert_log("报税密码错误，请及时修改")
                    self.post_data(self.tax_password_url,{'corpid':self.corpid,'pwd':'0','msg':'报税密码错误，请及时修改'})
                    driver.quit()
                    return False
                print('输错密码')    
                return self.login_action(login_times)
        except :
            pass
        
        # 判断是否登录成功
        try:
            driver.execute_script('layer.closeAll()')
            login_open = driver.find_element_by_id("login")
            if login_open:
                print('登录失败，重新登录')
                return self.login_action(login_times)
        except :
            pass
        return True



    # 解析验证码，直到获取到一个结果为止        
    def parse_action(self):
        #保存验证码图片到本地 并识别
        htool = HTool()
        local_img = htool.save_ercode_img(self.driver)
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
        except :
            pass

    # 使用driver post获取数据
    def post_data(self,url,data):
        self.get_cookie()
        htool = HTool()
        post_res = htool.post_data(self._cookie,url,data)
        return post_res

    # 使用driver get获取数据
    def get_data(self,url):
        self.get_cookie()
        htool = HTool()
        post_res = htool.get_data(self._cookie,url)
        return post_res

    def get_cookie(self):
        # if self._cookie:
        #     return

        cookies = self.driver.get_cookies()
        self._cookie = ''
        for item in cookies:
            self._cookie = self._cookie + item['name']+'='+item['value']+';'
   

    # 执行操作
    def driver_auto_action(self):
        ac = self.action.split('+')
        msg = []
        for a in ac:
            # if a == '1':
            #     msg.append(self.syn_user_total())
            if a == '2':
                self.insert_log('更新登记信息')
                msg.append(self.get_comp_info())
            if a == '3':
                self.insert_log('更新税费（种）认定信息')
                msg.append(self.get_tax_info())
            if a == '4':
                self.insert_log('更新银行登记信息')
                msg.append(self.get_bank_info())
            if a == '5':
                self.insert_log('更新报税信息')
                msg.append(self.get_tax_detail())
            if a == '6':
                self.insert_log('更新社保信息')
                msg.append(self.get_sb_detail())    
        self.driver.quit()        
        return self.corpname + ':' +','.join(msg)

    # 获取申报统计数据
    def syn_user_total(self):
        ret_msg = '获取申报统计数据失败'
        try:
            data = {'sbrqq': self.sbrqq, 'sbrqz': self.sbrqz}
            post_res = self.post_data(self.tax_data_url,data)
            res = self.get_qmld(post_res)
            if res:
                print('上传申报统计数据')
                # print(str(res))
                syn_res = self.post_data(self.tax_send_url,{'data':str(res),'corpid':self.corpid})
                if syn_res.status_code == 200:
                    ret_msg = '获取申报统计数据成功'
        except:
            pass

        return ret_msg

    # 公司登记信息
    def get_comp_info(self):
        ret_msg = '获取登记信息失败'
        try:
            comp = self.get_data(self.comp_info_url)
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
                syn_res = self.post_data(self.tax_corp_info_url,{'info':str(rt_dict),'corpid':self.corpid})
                if syn_res.status_code == 200:
                    ret_msg = '获取登记信息成功'
        except:
            pass
        return ret_msg

    # 税费（种）认定信息 
    def get_tax_info(self):
        ret_msg = '获取税费（种）认定信息失败'
        try:
            tax_info = self.get_data(self.tax_info_url)
            if tax_info:
                tax_node = BeautifulSoup(tax_info.text,'lxml')
                tax_array = tax_node.find(id='tableTest2').find('tbody').find_all('tr')
                rt_dict = []

                for node in tax_array:
                    td_arr = node.get_text().strip('\n')
                    rt_dict.append(td_arr.split('\n'))

                print('税费（种）认定信息')
                print(rt_dict)
                syn_res = self.post_data(self.tax_confirm_info_url,{'info':str(rt_dict),'corpid':self.corpid})
                if syn_res.status_code == 200:
                    ret_msg = '获取税费（种）认定信息成功'
        except:
            pass
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
        data = {'sbrqq': self.sbrqq, 'sbrqz': self.sbrqz}
        ret_msg = '获取申报统计数据失败'
        try:
            sb_data = self.post_data(self.tax_data_url,data)
        except:
            return ret_msg
        htool = HTool()

        if sb_data and sb_data.status_code == 200:
            try:
                tax_json = json.loads(sb_data.text)
            except:
                logging.error(self.corpname+": 获取申报数据失败,解析统计数据页面出错")
                return "获取申报数据失败,解析统计数据页面出错"
            
            rt = []
            # 解析title的模板
            parse_common_temp = json.loads(self.template['common'])
            load_config = json.loads(self.template['template'])
            try:
                # 解析统计数据，获取详情与解析模板
                for d in tax_json['data']:
                    # 匹配模板关键词找到解析模板
                    parse_match_temp = {}
                    parse_common_data = {}
                    for temp in load_config:
                        if self.check_keyword_in_temp(temp['keyword'],d['YZPZZL_MC']):
                            print(d['YZPZZL_MC'])
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
                    # print(link)
                    if parse_match_temp:
                        # 获取报税详情
                        sb_data = self.get_data(link)
                        if sb_data.status_code == 200:
                            # 残疾保障金页面数据需要提交form跳转页面获取
                            # if parse_match_temp['temp_id'] == '3':
                            #     sb_data = self.new_tax_page(sb_data.text)
                            
                            initData = re.search(r''+parse_match_temp['re_match_name']+'.{10,};',sb_data.text).group(0)
                            initData = initData.replace(parse_match_temp['re_match_name'],'').strip("\";'")
        
                            row_detail = self.parseTax(initData,parse_match_temp,parse_common_data)
                        # print(row_detail)
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
                            logging.error("待解析的税种模板(%s)不存在！请注意及时添加" % d['YZPZZL_MC'])
                            pass
            

                # print(json.dumps(rt))
                res = self.post_data(self.tax_update_url,{"corpid":self.corpid,"data":json.dumps(rt)})
                if res.status_code == 200:
                    res_text = json.loads(res.text)
                    if res_text['code'] != 0:
                        self.status_count("faild_num")
                        logging.error(self.corpname+":获取申报信息失败 "+res_text['text'])
                    
                    return res_text['text']
            except:
                pass

        else:
            pass
        logging.error(self.corpname+":获取申报信息失败")
        
        return ret_msg

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
    #     new_page = self.post_data(self.new_tax_url,submit_form)
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
            json_data = json.loads(data)
        except:
            logging.error("解析json数据错误 %s" % data)
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
                logging.error('解析通用数据json错误')
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
                logging.error("未找到解析印花税的方法，请及时检查")
                # print(data)
            if type(match_rows) == dict:
                match_rows = [match_rows]

        # 企业所得税B类json
        if template['temp_id'] == '3':
            if 'sb_sds_jmhd_18yjnd' in json_data:
                match_rows = json_data['sb_sds_jmhd_18yjnd']
            else:
                logging.error("未找到解析B类报表的方法 %s" % data)
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
                logging.error("未找到解析附加税数据的方法 %s" % data)
            
            if type(match_rows) == dict:
               match_rows = [match_rows]

        # 企业所得税A类json
        if template['temp_id'] == '5':
            if 'qysdsczzsyjdSbbdxxVO' in json_data:
                match_rows = json_data['qysdsczzsyjdSbbdxxVO']['A200000Ywbd']['sbbxxForm']
            elif 'sb_sds_jmcz_18yjd' in json_data:
                match_rows = json_data['sb_sds_jmcz_18yjd']
            else:
                logging.error("未找到解析A类报表的方法 %s" % data)
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
                logging.error("未找到解析增值税纳税的方法 %s" % data)

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
                    logging.error('解析详情数据失败')
                    pass
            parse_data = dict(parse_common_data,**parse_data)
            return_data.append(parse_data)

        parse_common_data['json_detail'] = json.dumps(return_data)
        return parse_common_data

    def get_sb_detail(self):
        sb_list = []
        err_msg,sb_list = self.get_sb_all(self.sbrqq,self.sbrqz,sb_list)
        
        if err_msg != '':
            return err_msg
        # print(err_msg,sb_list)
        
        if len(sb_list) == 0:
            return '获取社保信息成功(为空)'
        
        res = self.post_data(self.tax_update_url,{"corpid":self.corpid,"data":json.dumps(sb_list)})
        print(json.dumps(sb_list))
        if res.status_code == 200:
            try:
                res_text = json.loads(res.text)
                print(res_text)
                if res_text['code'] != 0:
                    self.status_count("faild_num")
                    logging.error(self.corpname+":获取社保信息失败 "+res_text['text'])
                
                return res_text['text']
            except: 
                return '上传社保信息失败'
        else:
            return '上传社保信息失败'

    # 递归获取时间范围内所有申报
    def get_sb_all(self,sbrqq,sbrqz,sb_list):
        # 获取单位核定申报与单位自主申报数据
        htool = HTool()
        rel_sbrqq,rel_sbrqz,end = htool.split_time(sbrqq,sbrqz)
        for i in range(0,2):
            data = {'sbrqq': rel_sbrqq, 'sbrqz': rel_sbrqz,'sbbzlDm':i}
            ret_msg = '获取社保信息失败'
            try:
                # print('获取数据',rel_sbrqq,rel_sbrqz)
                sb_data = self.post_data(self.sb_url,data)
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
                self.insert_log('请求社保接口出错')
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
        sb_data = self.get_data(link)
        
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
        # sb_data = self.post_data(self.tax_data_url,{'sbrqq':'2018-11-01','sbrqz':'2019-10-14'})
        htool = HTool()
        if(sb_data):
            tax_json = json.loads(sb_data.text)
            rt = []
            for d in tax_json['data']:
                if '一般纳税人适用' in d['YZPZZL_MC']:
                    link = htool.open_cell(d)
                    sb_data = self.get_data(link)
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
        try:
            bank_info = self.get_data(self.tax_sky_url)
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
                post_res = self.post_data(self.bank_update_url,{"corpid":self.corpid,"bank_list":str(rt_bank)})
                if post_res.status_code == 200:
                    ret_msg = '更新银行登记信息成功'
            print(str(rt_bank))

        except:
            pass
        return ret_msg

    def insert_log(self,msg,site = 0):
        self.lb.insert(site, ' '+time.strftime("%H:%M:%S", time.localtime())+' - '+msg)