# -*- coding: UTF-8 -*- 
from HTool import HTool
import json
import sys
import re

class Test:
    def __init__(self):
        self._cookie = 'UM_distinctid=171bae57eae353-08300d7c6a0d86-3a36510f-1fa400-171bae57eafea; aisino-never-guide=Y; aisino-wsbs-session=bcb55c05-02d0-4b83-a64a-d99644c748c4; CNZZDATA1277373975=269526059-1587975113-%7C1590641524; JSESSIONID=C7EC385B7FF28C9632A625743692DA07'
        # corp_list = "55||安徽一半一伴咖啡品牌管理有限公司 ||91340100094822207C||wcy123456||2019-08-01||2019-12-01||5"
        # corp_list = "64||安徽百胜医疗管理有限公司 ||91340100094822207C||wcy123456||2019-01-01||2019-12-07||5"
        corp_list = "936||合肥市汇巨装饰工程有限公司 ||91340100MA2MU4JX6P||wcy123456||2019-01-01||2019-12-07||5"
        self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action = corp_list.split('||',7)
        self.htool = HTool()
        self.config = self.htool.rt_config()
        self.tax_update_url = self.config['link']['tax_update_url']
        self.tax_data_url = self.config['link']['tax_data_url']
        self.sb_url = self.config['link']['sb_data_url']
        self.tax_kk_url = self.config['link']['tax_kk_url']
        self.net_bank_url = self.config['link']['net_bank_url']
        self.template = self.config['tax_template']

    # 获取扣款列表及网银列表
    def get_tax_kk_list(self):
        # data = {'swjgdm': '13401030000'}
        # kk_data = self.post_data(self.tax_kk_url,data)
        # print(kk_data.text)
        # 网银信息
        bank_data = self.post_data(self.net_bank_url,{})
        print(bank_data.text)


    def get_tax_detail(self):
        data = {'sbrqq': '2019-01-01','sbrqz': '2019-03-01','zsxmDm': '10104'}
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
            print(tax_json)
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

                    print(link)    
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
                            print("待解析的税种模板(%s)不存在！请注意及时添加" % d['YZPZZL_MC'])
                            pass
            

                # print(json.dumps(rt))
                res = self.post_data(self.tax_update_url,{"corpid":self.corpid,"data":json.dumps(rt)})
                if res.status_code == 200:
                    res_text = json.loads(res.text)
                    if res_text['code'] != 0:
                        self.status_count("faild_num")
                        print(self.corpname+":获取申报信息失败 "+res_text['text'])
                    
                    return res_text['text']
            except:
                pass

        else:
            pass
        print(self.corpname+":获取申报信息失败")
        
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
        res = self.post_data(self.tax_update_url,{"corpid":self.corpid,"data":json.dumps(sb_list)})
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


   

test = Test()
# res = test.get_sb_detail()
# print(res)
test.get_tax_kk_list()