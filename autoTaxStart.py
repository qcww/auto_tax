#coding=utf-8

import requests
import json
import websocket
import time
import tkinter as tk
import configparser
import threading
import sys
import tkinter.messagebox
from TaxSite import TaxSite
from HTool import HTool
from tkinter import simpledialog
from tkinter import StringVar
from tkinter import IntVar


class AutoTax:

    def __init__(self):
        window = tk.Tk()
        window.geometry('600x470')  # 这里的乘是小x
        sb = tk.Scrollbar(window)
        sb.pack(side=tk.RIGHT,fill=tk.Y)
        # 日志显示框与下滑块
        self.lb = lb = tk.Listbox(window, yscrollcommand=sb.set,width=65,height=22)
        self.insert_log('启动成功')
        lb.place(x=15, y=15)
        sb.config(command=lb.yview)
        self.run_text = StringVar()
        self.run_text.set('启动应用')

        self.status_bar = {"receive_num" : StringVar(value='已接收:0'),"success_num" : StringVar(value='成功:0'),"faild_num" : StringVar(value='失败:0'),"pass_err_num":StringVar(value='密码错误:0'),"his_err_num":StringVar()}

        # status_bar["receive_num"].set('已接收:0')
        # status_bar["success_num"].set('成功:0')
        # status_bar["faild_num"].set('失败:0')
        # status_bar["pass_err_num"].set('密码错误:0')

        # 添加与采集按钮
        tk.Button(window, textvariable=self.run_text, width=10, height=1, command=self.start_app).place(x=490, y=15)
        tk.Button(window, text="失败重试", width=10, height=1, command=self.retry).place(x=490, y=50)

        # 成功个数与失败个数
        tk.Label(window,textvariable=self.status_bar["receive_num"]).place(x=15,y=440)
        tk.Label(window,textvariable=self.status_bar["success_num"],foreground="green").place(x=85,y=440)
        tk.Label(window,textvariable=self.status_bar["faild_num"],foreground="red").place(x=155,y=440)
        tk.Label(window,textvariable=self.status_bar["pass_err_num"],foreground="red").place(x=225,y=440)
        tk.Label(window,textvariable=self.status_bar["his_err_num"],foreground="red").place(x=315,y=440)
        menubar = tk.Menu(window)

        editmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='操作', menu=editmenu)
        editmenu.add_command(label='清空待处理',command=self.clear_log)
        window.config(menu=menubar)

        self.htool = HTool()
        self.config = self.htool.rt_config()

        self.err_arr = {}
        err_list = self.htool.get_config('scrap','err_list')
        if err_list:
            self.err_arr = json.loads(err_list)

        self.status_bar['his_err_num'].set("待处理：%s" % len(self.err_arr))

        self.insert_log('读取配置文件成功')
        self.run_status = False
        self.retry_status = False
        self.is_running = False

        self.tax_site = TaxSite(self.lb,self.status_bar)

        window.title('合肥鑫山财务管理有限公司-税务数据采集客户端 - v'+self.config['clien']['version'])
        # 第5步，主窗口循环显示
        window.resizable(0,0)
        window.mainloop()

    def clear_log(self):
        self.htool.set_config('scrap','err_list','')
        tkinter.messagebox.showinfo('提示','清除成功！')
        self.err_arr = {}
        self.status_bar['his_err_num'].set("待处理：%s" % len(self.err_arr))

    def syn_user_data(self,corp_data):
        if corp_data == None:
            return False
        print(corp_data)
        self.is_running = True
        corpid = self.tax_site.set_corp(corp_data)

        self.tax_site.open_browser()
        login_res = self.tax_site.login()
        # 登录失败，跳过
        if login_res == False:
            rt = '登录失败'
        else:
            self.tax_site.page_init()
            rt = self.tax_site.driver_auto_action()
            
        if '成功' in rt and '失败' not in rt:
            if corpid in self.err_arr:
                del self.err_arr[corpid]
            self.tax_site.status_count("success_num")
        else:
            self.err_arr[corpid] = corp_data
            self.tax_site.status_count("faild_num")
        self.is_running = False
        self.status_bar['his_err_num'].set("待处理：%s" % len(self.err_arr))
        self.htool.set_config('scrap','err_list',json.dumps(self.err_arr))
        return rt

    def create_websocket(self):
        def on_message(ws, message):
            msg = json.loads(message)
            if msg['type'] == 'action' and msg['data'] != '':
                self.lb.insert(0, "")
                rt = self.syn_user_data(msg['data'])
                reply = '{"type":"reply","isfree":1,"room_id":"%s","data":"%s","client_name":"%s","request_client_id":"%s"}' % (self.config['clien']['room_id'],rt,self.config['clien']['name'],msg['request_client_id'])
                self.insert_log(rt)
                ws.send(reply)

        def on_error(ws, error):
            self.run_status = False
            self.insert_log(error)


        def on_close(ws):
            self.run_status = False
            self.lb.insert(0,'')
            self.insert_log('连接已断开')
            self.run_text.set('启动应用')

        def on_open(ws):
            self.run_status = True
            self.lb.insert(0,'')
            self.insert_log('服务器连接成功')
            ws.send('{"type":"login","room_id":"%s","client_name":"%s"}' % (self.config['clien']['room_id'],self.config['clien']['name']))

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = on_open
        self.ws = ws
        ws.run_forever()

    def insert_log(self,msg,site = 0):
        self.lb.insert(site, ' '+time.strftime("%H:%M:%S", time.localtime())+' - '+msg)

    def start_app(self):
        self.run_status = bool(1 - self.run_status)
        if hasattr(self,'mythread') == False:
            self.mythread = threading.Thread(target=self.create_websocket)
            self.cond = threading.Condition() # 锁
            self.mythread.start()

        if self.run_status == True:
            # self.run_text.set('启动中')
            self.run_text.set('运行中')
        else:
            delattr(self,'mythread')
            self.ws.close()
            self.run_text.set('停止中')
        
    def retry_action(self):
        retry_list = self.err_arr.copy()
        for re in retry_list:
            print(retry_list[re])
            self.lb.insert(0, "")
            rt = self.syn_user_data(retry_list[re])
            self.insert_log(rt)
        self.retry_status = False    

    def retry(self):
        # 如果是正在运行的话结束脚本
        if self.run_status == True:
            self.start_app()
        if len(self.err_arr) == 0:
            tkinter.messagebox.showinfo('提示','待重试数据为空')
            return

        if self.is_running == True:
            tkinter.messagebox.showinfo('提示','请等待当前脚本执行结束后重试')
            return

        if self.retry_status == True:
            tkinter.messagebox.showinfo('提示','正在重试')
            return
        self.retry_status = True
        mythread = threading.Thread(target=self.retry_action)
        mythread.start()

auto = AutoTax()