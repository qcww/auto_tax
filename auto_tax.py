# -*- coding: utf-8 -*- 

import wx
import wx.adv
import ui
import time
import configparser
import datetime
import requests
import re
import os
import sys
import regedit
import win32com.client
import websocket
import threading
import json
import requests
import json
import websocket

from TaxSite import TaxSite
from HTool import HTool

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='mondrian.ico', type=wx.BITMAP_TYPE_ICO), '发票辅助工具')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftDClick)
 
    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
           self.frame.Iconize(False)
        if not self.frame.IsShown():
           self.frame.Show(True)
        self.frame.Raise()
 
    def OnClose(self, event):
        self.frame.Destroy()
        self.Destroy()

    def OnConfig(self, event):
        pass

    def OnAbout(self, event):
        pass

    # Menu数据
    def setMenuItemData(self):
        # return (("关闭", self.OnClose))
         return (("配置", self.OnConfig), ("退出", self.OnClose))
    
    # 创建菜单
    def CreatePopupMenu(self):
        menu = wx.Menu()
        for itemName, itemHandler in self.setMenuItemData():
            if not itemName:    # itemName为空就添加分隔符
                menu.AppendSeparator()
                continue
            menuItem = wx.MenuItem(None, wx.ID_ANY, text=itemName, kind=wx.ITEM_NORMAL) # 创建菜单项
            menu.Append(menuItem)                                                   # 将菜单项添加到菜单
            self.Bind(wx.EVT_MENU, itemHandler, menuItem)
        return menu


class Ep(ui.MainMenu):
    def __init__(self, parent=None, id=wx.ID_ANY, title='发票辅助工具'):
        ui.MainMenu.__init__(self, parent)
       
        self.SetIcon(wx.Icon('mondrian.ico', wx.BITMAP_TYPE_ICO))
        panel = wx.Panel(self, wx.ID_ANY)
        button = wx.Button(panel, wx.ID_ANY, 'Hide Frame', pos=(60, 60))
       
        sizer = wx.BoxSizer()
        sizer.Add(button, 0)
        panel.SetSizer(sizer)
        self.taskBarIcon = TaskBarIcon(self)

        self.htool = HTool()
        self.config = self.htool.rt_config()
        self.task_arr = []

        self.tax_site = TaxSite(self)
       
        # bind event
        self.Bind(wx.EVT_BUTTON, self.OnHide, button)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) # 最小化事件绑定

    def OnHide(self, event):
        self.Hide()

    def OnIconfiy(self, event):
        # wx.MessageBox('Frame has been iconized!', 'Prompt')
        event.Skip()

    def OnClose(self, event):
        self.Hide()

    def retry( self, event ):
        self.running_index = -1

    def add_kk_task( self, event ):
        self.auto_kk = bool(1-self.auto_kk)
        self.kk_btn.SetValue(self.auto_kk)
        if self.auto_kk == True:
            self.kk_btn.SetLabel('正在扣款')
        else:
            self.kk_btn.SetLabel('扣款')

    def add_auto_tax_task(self,event):
        self.auto_tax = bool(1-self.auto_tax)
        self.report_btn.SetValue(self.auto_tax)
        if self.auto_tax == True:
            self.report_btn.SetLabel('正在报税')
        else:
            self.report_btn.SetLabel('报税')

    def add_agent_task(self,event):
        self.auto_dkfp = bool(1-self.auto_dkfp)
        self.agent_btn.SetValue(self.auto_dkfp)
        if self.auto_dkfp == True:
            self.agent_btn.SetLabel('获取代开')
        else:
            self.agent_btn.SetLabel('代开发票')

    def start(self):
        self.running_index = -1
        self.auto_kk = False
        self.auto_tax = False
        self.auto_dkfp = False

        # self.set_status('已准备')

        print('辅助工具已打开')

        self.connect_service()
        self.check_task()
        return True

    def set_status(self,text,i=0):
        self.SetStatusText(text,i)

    def connect_service(self):
        # self.run_status = bool(1 - self.run_status)
        if hasattr(self,'mythread') == False:
            self.mythread = threading.Thread(target=self.create_websocket)
            self.cond = threading.Condition() # 锁
            self.mythread.start()
        elif self.check_usb.is_alive() == False:
            delattr(self,'mythread')
            return self.connect_service()

    def check_task(self):
        if hasattr(self,'task_check') == False:
            self.task_check = threading.Thread(target=self.check_task_win)
            self.cond = threading.Condition() # 锁
            self.task_check.start()
        elif self.task_check.is_alive() == False:
            delattr(self,'task_check')
            return self.check_task()

    # 保持运行检查未完成任务
    def check_task_win(self):
        while True:
            # 同步数据
            if len(self.task_arr) == 0:
                self.running_index = -1
            # 有新任务
            if self.running_index <= (len(self.task_arr)-2) and len(self.task_arr) > 0:
                self.running_index += 1
                # print(self.running_index,self.task_arr,len(self.task_arr))
                self.syn_user_data(self.task_arr[self.running_index])
            else:
                if self.auto_kk == True:
                    self.add_log('自动获取未扣款数据')
                    # print('自动执行批量处理')
                    self.add_task_kk_bundle()
                if self.auto_tax == True:
                    self.add_log('自动获取未报税数据')
                    # print('自动执行批量处理')
                    self.add_task_tax_bundle()
                if self.auto_dkfp == True:
                    self.add_log('自动获取代开发票数据')
                    self.add_task_dkfp_bundle()    
            time.sleep(5)


    def create_websocket(self):
        def on_message(ws, message):
            msg = json.loads(message)
            if msg['type'] == 'action' and msg['data'] != '':
                print('收到消息',msg)
                add_task = self.add_task(msg['data'])
                reply = '{"type":"reply","isfree":1,"room_id":"%s","data":"%s","client_name":"%s","request_client_id":"%s"}' % (self.config['clien']['room_id'],add_task,self.config['clien']['name'],msg['request_client_id'])
                print('回复消息',reply)
                ws.send(reply)

        def on_error(ws, error):
            self.run_status = False
            time.sleep(5)
            self.create_websocket()


        def on_close(ws):
            self.run_status = False
            self.add_log('')
            self.add_log('连接已断开')
            time.sleep(5)
            self.create_websocket()

        def on_open(ws):
            self.run_status = True
            self.add_log('')
            self.add_log('服务器连接成功')
            self.set_status('已准备')
            ws.send('{"type":"login","room_id":"%s","client_name":"%s"}' % (self.config['clien']['room_id'],self.config['clien']['name']))

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = on_open
        self.ws = ws
        ws.run_forever()

    # 回复浏览器消息
    def reply_explore(self,request_client_id,text):
        print('回复消息',request_client_id)
        self.ws.send('{"type":"reply","room_id":"%s","request_client_id":"%s","client_name":"%s","data":"%s"}' % (self.config['client']['room_id'],request_client_id,self.uid,text))

    # 添加日志
    def add_log(self,text):
        log_text = ''
        if text != '':
            log_text = "%s %s" % (time.strftime("%H:%M", time.localtime()),text)
        self.log_list.InsertItems([log_text],0)

    def syn_user_data(self,corp_data):
        # try:
        if corp_data == None:
            return False        
        corpid = self.tax_site.set_corp(corp_data)

        self.tax_site.open_browser()
        login_res = self.tax_site.login()
        # 登录失败，跳过
        if login_res == False:
            return False
        else:
            self.tax_site.page_init()
            self.tax_site.driver_auto_action()

    # 添加任务
    def add_task(self,corp_list):
        # 单独处理批量操作
        if corp_list == 'bundle||7':
            self.auto_kk = True
            return '自动执行批量扣款'
        elif corp_list == 'bundle||-7':
            self.auto_kk = False
            return '自动扣款任务已暂停'
        if corp_list == 'bundle||9':
            self.auto_tax = True
            return '自动执行批量报税'
        elif corp_list == 'bundle||-9':
            self.auto_tax = False
            return '自动报税任务已暂停'
        if corp_list == 'bundle||10':
            self.auto_dkfp = True
            return '自动执行批量获取代开具发票'
        elif corp_list == 'bundle||-10':
            self.auto_dkfp = False
            return '自动获取代开具发票任务已暂停'
        # if corp_list not in self.task_arr:
        #     self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action = corp_list.split('||',7)
        #     self.task_list.InsertItems(["%s %s" % (time.strftime("%M:%S", time.localtime()),"收到请求:"+self.corpname + " " + self.action)],0)
        #     self.task_arr.append(corp_list)
        #     print('任务信息',corp_list)
        #     return '任务添加成功'
        # else:
        #     return '该任务已在任务列表里'
        self.corpid, self.corpname, self.credit_code, self.pwd, self.sbrqq, self.sbrqz,self.action = corp_list.split('||',7)
        self.task_list.InsertItems(["%s %s" % (time.strftime("%H:%M", time.localtime()),"收到请求:"+self.corpname + " " + self.action)],0)
        self.task_arr.append(corp_list)
        print('任务信息',corp_list)
        return '任务添加成功'

    # 通过批处理添加扣款任务
    def add_task_kk_bundle(self):
        kk_list = self.tax_site.get_kk_data()
        # 没有任务了，自动停止批量操作
        if len(kk_list['rows']) == 0:
            self.add_log('批量请求扣款数据为空，自动暂停')
            self.auto_kk = False
            self.kk_btn.SetValue(self.auto_kk)
            self.kk_btn.SetLabel('扣款')

        for re in kk_list['rows']:
            post = (re['corpid'],re['corpname'],re['credit_code'],re['tax_pwd_gs'],"","","7")
            post_data = '||'.join(post)
            self.add_task(post_data)
        ret = '剩余可扣款数:' + kk_list['total']
        self.set_status(ret)
        return ret

    # 通过批处理添加报税任务
    def add_task_tax_bundle(self):
        print('自动申报')
        tax_list = self.tax_site.get_tax_data()
        # print('tax_list',tax_list)
        # 没有任务了，自动停止批量操作
        if len(tax_list['rows']) == 0:
            self.add_log('批量请求报税数据为空，自动暂停')
            self.auto_tax = False
            self.report_btn.SetValue(self.auto_tax)
            self.report_btn.SetLabel('报税')

        for re in tax_list['rows']:
            post = (re['corpid'],re['corpname'],re['credit_code'],re['tax_pwd_gs'],"","","9")
            post_data = '||'.join(post)
            self.add_task(post_data)
        ret = '剩余可报税数:' + tax_list['total']
        self.set_status(ret)
        return ret

    def add_task_dkfp_bundle(self):
        print('自动获取代开发票')
        tax_list = self.tax_site.get_dkjfp_data()
        # print('tax_list',tax_list)
        # 没有任务了，自动停止批量操作
        if len(tax_list['rows']) == 0:
            self.add_log('批量请求待上传代开具发票企业为空，自动暂停')
            self.auto_dkfp = False
            self.agent_btn.SetValue(self.auto_dkfp)
            self.agent_btn.SetLabel('代开发票')

        for re in tax_list['rows']:
            post = (re['corpid'],re['corpname'],re['credit_code'],re['tax_pwd_gs'],"","","10")
            post_data = '||'.join(post)
            self.add_task(post_data)
        ret = '剩余待上传开具发票公司:' + tax_list['total']
        self.set_status(ret)
        return ret

    # 执行成功,删除任务
    def remove_task(self):
        self.task_arr.pop(self.running_index)
        self.running_index -= 1
        self.task_list.Delete(0)

    def post_link(self,link,post_data):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
        try:
            req = requests.post(link, data=post_data, headers=headers)
            resp = req.json()
            return resp
        except:
            return {"code":500,"text":"网络异常，请求失败"}

if '.exe' in sys.argv[0]:
    try:
        regedit.set_client_path()
        # 设置开机启动
        pp = re.findall(r'.[^\\]*\.exe',sys.argv[0])
        ename = pp[0].replace('\\','')
        main_app = regedit.get_client_path() + '\\' + ename + " /autorun"
        if regedit.add_auto_run(main_app) == False:
            print('设置开机启动失败')
        else:
            print('设置开机启动成功')
    except:
        print('设置开机启动失败')

work_space = regedit.get_client_path()
if work_space != '':
    try:
        os.chdir(work_space)
    except:
        print('设置路径出错')    

app = wx.App()
frame = Ep(None)
ready = frame.start()
if ready == False:
    sys.exit()

if '/autorun' in sys.argv:
    show_fram = False
else:
    show_fram = True

frame.Show(show_fram)
app.MainLoop()