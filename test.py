# -*- coding: UTF-8 -*- 
from HTool import HTool
import json
import sys
import re
import time
import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance

class Test:
    def __init__(self):
        self._cookie = 'UM_distinctid=171bae57eae353-08300d7c6a0d86-3a36510f-1fa400-171bae57eafea; aisino-never-guide=Y; JSESSIONID=420836A233E147CE05384CA4B1B7EDCA; aisino-wsbs-session=f07b09ea-fc0e-4e9c-ae4e-e6c558371794; CNZZDATA1277373975=269526059-1587975113-%7C1592390772'
        # corp_list = "55||安徽一半一伴咖啡品牌管理有限公司 ||91340100094822207C||wcy123456||2019-08-01||2019-12-01||5"
        # corp_list = "64||安徽百胜医疗管理有限公司 ||91340100094822207C||wcy123456||2019-01-01||2019-12-07||5"
        corp_list = "3491||合肥崇武商贸有限公司||91340100MA2MW65Q6Y||wcy123456||2020-05-01||2020-06-06||5"
        self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action = corp_list.split('||',7)
        self.htool = HTool()
        self.config = self.htool.rt_config()
        self.tax_update_url = self.config['link']['tax_update_url']
        self.tax_data_url = self.config['link']['tax_data_url']
        self.dkfp_data_url = self.config['link']['dkfp_data_url']
        self.sb_url = self.config['link']['sb_data_url']
        self.tax_kk_url = self.config['link']['tax_kk_url']
        self.net_bank_url = self.config['link']['net_bank_url']
        self.template = self.config['tax_template']
        self.kk_update_url = self.config['link']['kk_update_url']
        self.bundle_kk_status_url = self.config['link']['bundle_kk_status_url']
        self.dkfp_detail_url = self.config['link']['dkfp_detail_url']
        self.ready_tax_url = self.config['link']['ready_tax_url']
        self.tax_info_url = self.config['link']['tax_info_url']
        self.tax_config_info = self.config['tax_config_info']
        self.zzfp_detail_url = self.config['link']['zzfp_detail_url']
        self.agent_invoice_url = self.config['link']['agent_invoice_url']
        self.agent_invoice_detail_url = self.config['link']['agent_invoice_detail_url']
        

    # 获取扣款列表及网银列表
    def get_tax_kk_list(self):
        # data = {'swjgdm': '13401030000'}
        # kk_data = self.post_data(self.tax_kk_url,data)
        # print(kk_data.text)
        # 网银信息
        bank_data = self.post_data(self.net_bank_url,{})
        print(bank_data.text)


    def get_tax_detail(self):
        data = {'sbrqq': '2020-06-01','sbrqz': '2020-06-06','zsxmDm': ''}
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
                return "获取申报数据失败,解析统计数据页面出错"
            
            rt = []
            # print(tax_json)
            # 解析title的模板
            parse_common_temp = json.loads(self.template['common'])
            load_config = json.loads(self.template['template'])
            # try:
            # 解析统计数据，获取详情与解析模板
            for d in tax_json['data']:
                # 匹配模板关键词找到解析模板
                parse_match_temp = {}
                parse_common_data = {}
                for temp in load_config:
                    if self.check_keyword_in_temp(temp['keyword'],d['YZPZZL_MC']):
                        # print(d['YZPZZL_MC'])
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

                if parse_match_temp:
                    # 获取报税详情
                    sb_data = self.get_data(link)

                    if sb_data.status_code == 200:
                        # 残疾保障金页面数据需要提交form跳转页面获取
                        if parse_match_temp['temp_id'] == '3':
                            sb_data = self.new_tax_page(sb_data.text)
                        
                        initData = re.search(r''+parse_match_temp['re_match_name']+'.{10,};',sb_data.text).group(0)
                        initData = initData.replace(parse_match_temp['re_match_name'],'').strip("\";'")
    
                        row_detail = self.parseTax(initData,parse_match_temp,parse_common_data)

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
                        print("待解析的税种模板(%s)不存在！请注意及时添加" % d['YZPZZL_MC'])
                        pass
        
            ss_data = self.ss_gl(rt)
            for ss_item in ss_data:
                fill_date_arr = ss_item.split('-')
                fill_date = "%s-%s-01" % (fill_date_arr[0],fill_date_arr[1])

                stop_date_arr = ss_data[ss_item][0]['stop_date'].split('-')
                period = "%s%s" % (stop_date_arr[0],stop_date_arr[1])

                res = self.post_data(self.tax_update_url,{"corpid":self.corpid,'period':period,'fill_date':fill_date,"msg":"自动更新[所属期：%s - 已申报税收数据]完成" % period,"data":json.dumps(ss_data[ss_item])})
                print('上传你结果',res.text)
                if res.status_code == 200:
                    res_text = json.loads(res.text)
                    if res_text['code'] != 0:
                        self.insert_log(self.corpname+":获取申报信息失败 "+res_text['text'])
                
            #     return res_text['text']
            # except:
            #     pass

        else:
            print(self.corpname+":获取申报信息失败")
            pass
        # print(self.corpname+":获取申报信息失败")
        
        return ret_msg

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

    # 检查当前关键词是否都在模板里匹配
    def check_keyword_in_temp(self,k,temp):
        k_arr = k.split("&")
        match_row = True
        for keyword in k_arr:
            if keyword not in temp:
                match_row = False
                break    
        return match_row    

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

    def get_sb_detail(self):
        sb_list = []
        err_msg,sb_list = self.get_sb_all(self.sbrqq,self.sbrqz,sb_list)
        
        if err_msg != '':
            return err_msg
        
        if len(sb_list) == 0:
            return '获取社保信息成功(为空)'
        else:
            # 数据重新归类
            print('数据重新归类')
            sb_list = self.sb_gl(sb_list)

        for sb_period in sb_list:
            sb_list[sb_period]['json_detail'] = '['+','.join(sb_list[sb_period]['json_detail'])+']'
            res = self.post_data(self.tax_update_url,{"corpid":self.corpid,'period':sb_list[sb_period]['period'],'fill_date':sb_list[sb_period]['fill_date'],"msg":"自动更新[所属期：%s - 已申报税收数据]完成" % sb_list[sb_period]['period'],"data":json.dumps([sb_list[sb_period]])})

            print(res.text)
            if res.status_code == 200:
                try:
                    res_text = json.loads(res.text)
                    
                    if res_text['code'] != 0:
                        print(self.corpname+":获取社保信息失败 "+res_text['text'])
                    
                    return res_text['text']
                except: 
                    return '上传社保信息失败'
            else:
                return '上传社保信息失败'

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
            tax_json = json.loads(sb_data.text)
            if sb_data and sb_data.status_code == 200:
                try:
                    tax_json = json.loads(sb_data.text)
                    print('解析数据',rel_sbrqq,rel_sbrqz)
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
                parse_common_data['json_detail'] = json.dumps({"jfrs":'3'})
                # print(d['ZSPMMC'])
                # parse_common_data['json_detail'] = self.get_sb_fee_num(link)
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

    # 使用driver post获取数据
    def post_data(self,url,data):
        htool = HTool()
        post_res = htool.post_data(self._cookie,url,data)
        return post_res

    # 使用driver get获取数据
    def get_data(self,url):
        htool = HTool()
        post_res = htool.get_data(self._cookie,url)
        return post_res


    # 重新更新缴款信息
    def update_kk_info(self,jkrqq = '',jkrqz = ''):
        if jkrqq == '':
            jkrqq = self.sbrqq
        if jkrqz == '':
            jkrqz = self.sbrqz

        data = {'jkrqq': jkrqq,'jkrqz': jkrqz,'ssqq': '','ssqz':'','uuid':''}
        ret_msg = '获取申报统计数据失败'
        self.insert_log('更新扣款状态')
        try:
            kk_data = self.post_data(self.kk_update_url,data)
        except:
            print(ret_msg)
            return ret_msg

        if kk_data and kk_data.status_code == 200:
            post_data = {}
            # 通用代码，执行到此步，默认通用项目已经扣除
            
            # try:
            tax_json = json.loads(kk_data.text)
            parse_data = tax_json['data'][0]
            kk_data = self.kk_gl(parse_data,jkrqq,jkrqz)
            ret_msg = ''
            for kk in kk_data:
                xmdm = ['BDA0610100']
                parse_data = kk_data[kk]
                # print('parse_data',parse_data)
                for it in parse_data:
                    if 'YZPZZL_DM' in it:
                        print('种类代码',it['YZPZZL_DM'])
                        xmdm.append(it['YZPZZL_DM'])
                        if 'TFRQ' in it:
                            jkrqq = jkrqz = it['TFRQ']
                        elif 'SJRQ_1' in it:
                            jkrqq = jkrqz = it['SJRQ_1']
                post_data['corpid'] = self.corpid
                post_data['jkrqq'] = jkrqq
                post_data['jkrqz'] = jkrqz
                post_data['json_data'] = json.dumps(list(set(xmdm)))
                # print(jkrqq)
                post_data['msg'] = '更新扣款状态 [缴款日期：%s] 成功' % jkrqq
                print('扣款信息更新提交数据',post_data)
                update_res = self.post_data(self.bundle_kk_status_url,post_data)
                if update_res.status_code == 200:
                    kk_json = json.loads(update_res.text)
                    err = kk_json['text']
                    ret_msg += err
                else:
                    err = '上传扣款数据时发生错误'
                    ret_msg += err
                self.insert_log(err)    
            return ret_msg
            # except:
            #     return "获取申报数据失败,解析统计数据页面出错"
 

        # post_data['json_data'] = json.dumps(list(set(xmdm)))
        # post_data['msg'] = '未缴款信息为空，重新更新扣款状态'
        # update_res = self.post_data(self.bundle_kk_status_url,post_data)
        # print('缴款代码',xmdm)
        # print('更新结果',update_res.text)
        post_data = {"corpid":315,"jkrqq":time.strftime("%Y-%m-01",time.localtime()),"jkrqz":time.strftime("%Y-%m-%d",time.localtime()),"json_data":"","msg":"你是我的小可爱"}
        update_res = self.post_data(self.bundle_kk_status_url,post_data)
        print(update_res.text)

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

    # 代开发票查询
    def dkfp_search(self):
        kjrq = time.strftime("%Y-%m-01",time.localtime())
        data = {'kjrqq': '2020-01-01','kjrqz': kjrq}
        ret_msg = '获取已代开发票数据失败'
        # try:
        # 发票开具信息查询
        dkfp_ret = self.post_data(self.dkfp_data_url,data)
       
        if dkfp_ret.status_code == 200:
            dkfp_data = json.loads(dkfp_ret.text)
            post_agent = self.post_data(self.agent_invoice_url,{"corpid":self.corpid,"rows_data":json.dumps(dkfp_data['data'])})
            print(post_agent.text)
            fp_detail = self.dkfp_detail(1)
            # print(fp_detail)
            post_fp = self.post_data(self.agent_invoice_detail_url,{"corpid":self.corpid,"rows_data":json.dumps(fp_detail)})
            # print(post_fp.text)
            # except:
            #     return ret_msg

    def dkfp_detail(self,pageNum):
        # 发票申请
        data = {'pageSize': '2','pageNum': pageNum,'formType':'A02'}
        ret_msg = '获取代开发票申请数据失败'
        # try:
        dkfp_data = self.post_data(self.dkfp_detail_url,data)
        if dkfp_data.status_code == 200:
            dkfp_json = json.loads(dkfp_data.text)
            # print(dkfp_json)
            if int(dkfp_json['data']['total']) > 0 and len(dkfp_json['data']['rows']) > 0:
                ret_json = []
                for dk in dkfp_json['data']['rows']:
                    app_time_arr = dk['createtime'].split('-')
                    if int(app_time_arr[0]) < 2020:
                        continue

                    d_link = self.zzfp_detail_url + dk['data_ID']
                    get_agent = self.get_data(d_link)
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
        # except:
        #     print('解析错误')
        #     return ret_msg


    # 税费（种）认定信息 
    def ready_tax_info(self):
        rt_dict = []
        tax_dict = {}
        already_tax = []
        htool = HTool()
        try:
            tax_info = self.get_data(self.tax_info_url)
            sbrqq = time.strftime("%Y-%m-01",time.localtime())
            sbrqz = time.strftime("%Y-%m-%d",time.localtime())
            data = {'sbrqq': sbrqq,'sbrqz': sbrqz,'zsxmDm': ''}
            ret_msg = '获取申报统计数据失败'
            try:
                sb_data = self.post_data(self.tax_data_url,data)
            except:
                return ret_msg

            htool = HTool()

            if sb_data and sb_data.status_code == 200:
                try:
                    tax_json = json.loads(sb_data.text)
                    tax_data = tax_json['data']
                    for tax_it in tax_data:
                        already_tax.append(tax_it['BDDM']+':'+tax_it['SKSSQQ'])
                except:
                    print('解析已申报数据出错')
                    return False
            else:
                print('获取已申报数据失败')
                return False        
            if tax_info:
                tax_node = BeautifulSoup(tax_info.text,'lxml')
                tax_array = tax_node.find(id='tableTest2').find('tbody').find_all('tr')
                
                aj_dict = ['1','4','7','10']
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
                    # 首先过滤掉本月
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

                    tax_bd = json.loads(self.tax_config_info['ah'])
                    for cf in tax_bd:
                        if it[2] in cf['keyword']:
                            sz_bddm = cf['bddm']
                            if ((sz_bddm + it[4]) not in tax_dict) and (sz_bddm+":"+ssqq not in already_tax):
                                tax_dict[(sz_bddm + it[4])] = {"bddm":sz_bddm,"ss_period":ss_period,"ssqq":ssqq,"tax_link":self.tax_config_info['sb_url_pre'] + "bddm=%s&ssqq=%s&ssqz=%s" % (sz_bddm,ssqq,ssqz)}

            # print(tax_dict,already_tax)
        except:
            print('读取解析税费种认定信息时发生错误')
            pass

        return tax_dict


    # 报税
    def tax_sb(self):
        data = {'gdslx': ''}
        ret_msg = ''
        # try:
        ready_tax = self.post_data(self.ready_tax_url,data)
        # print(ready_tax.text)
        if ready_tax.status_code == 200:
            tax_json = json.loads(ready_tax.text)
            # print(tax_json['data']) 
            # 解析链接中绑定代码分批次报税
            tax_sb_it = {}
            for tax in tax_json['data']:
                parse_link = urlparse(tax['url'],'',True)
                # print(parse_link.query)

                pp = parse_qs(parse_link.query)
                # print(pp)
                # 确定有哪些申报项目及品目
                bddm = pp['bddm'][0]
                if 'zspmDm' in pp:
                    pmdm = pp['zspmDm'][0]
                else:
                    pmdm = ''    
                if bddm not in tax_sb_it:
                    tax_sb_it[bddm] = [pmdm]
                    self.do_tax_sb(tax['url'],bddm)

                # split_result=urlsplit(url)
                # print(split_result)
        # except:
        #     ret_msg = '获取代办事项失败'
        #     return ret_msg

    def do_tax_sb(self,tax_url,bddm):
        # 打开网页，获取数据
        # 通用申报
        if bddm == 'TYSB100':
            print(bddm)
            self.driver.get(tax_url)
            sleep(3)
            sb_data = self.driver.execute_script("return $('#sbbTable').table('getData');")
            print('待申报数据',sb_data)
        else:
            print(bddm,'对应的报税方法正在完善')    

    def insert_log(self,msg):
        print(msg)    
   

test = Test()
# res = test.get_sb_detail()
# print(res)
# test.get_tax_kk_list()
# test.update_kk_info()
# test.testInt()
# test.get_tax_detail()

# 税务局代开发票
# test.dkfp_search()

# 报税
# test.tax_sb()
# htool = HTool()
# cc = htool.month_get(3)
# print(cc)
# ss = htool.last_day_of_month()
# print(ss)
# tax = test.ready_tax_info()
# print(tax)

def convert_img():
    img = Image.open('yjbot.png').crop((0, 0, 60, 30))
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            print(pixels[i,j])
            if (pixels[i,j][0] > 100 or pixels[i,j][1] > 100 or pixels[i,j][2] > 100) and pixels[i,j] != (0,0,0):
                pixels[i,j] = (254, 255, 255)
                # if pixels[i,j] == (225, 225, 225):
                #     pixels[i,j] = (1)
                # elif pixels[i,j] == (76, 76, 76):
                #     pixels [i,j] = (2)
                # else: pixels[i,j] = (1)
            else:
                pixels[i,j] = (0, 0, 0)
            # pixels[i,j] = (254, 255, 255)
    img.save('example.png')

    # img = Image.open(screenImg).crop((left, top, right, bottom))
    #下面对图片做了一些处理
    # img = img.convert('RGBA')  # 转换模式：L | RGB
    # img = img.convert('L')  # 转换模式：L | RGB
    # img = ImageEnhance.Contrast(img)  # 增强对比度
    # img = img.enhance(2.0)  # 增加饱和度
    # img.save('example.png')

convert_img()