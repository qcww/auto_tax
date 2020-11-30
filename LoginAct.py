# -*- coding: utf-8 -*- 

import wx
import wx.adv
import ui
import time
import configparser
import datetime
import sys
import win32com.client
import threading
from SbSite import SbExport
from TaxSite import TaxSite
from HTool import HTool

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='bitbug_favicon.ico', type=wx.BITMAP_TYPE_ICO), '异步登录程序')
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


class Ep(ui.MainLogin):
    def __init__(self, parent=None, id=wx.ID_ANY, title='异步登录程序'):
        ui.MainLogin.__init__(self, parent)
       
        self.SetIcon(wx.Icon('bitbug_favicon.ico', wx.BITMAP_TYPE_ICO))
        panel = wx.Panel(self, wx.ID_ANY)
        button = wx.Button(panel, wx.ID_ANY, 'Hide Frame', pos=(60, 60))
       
        sizer = wx.BoxSizer()
        sizer.Add(button, 0)
        panel.SetSizer(sizer)
        self.taskBarIcon = TaskBarIcon(self)

        self.htool = HTool()
        self.config = self.htool.rt_config()

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

    def start(self):
        self.check_task()
        return True

    def check_task(self):
        if hasattr(self,'task_check') == False:
            self.task_check = threading.Thread(target=self.check_task_win)
            self.cond = threading.Condition() # 锁
            self.task_check.start()
        elif self.task_check.is_alive() == False:
            delattr(self,'task_check')
            return self.check_task()

    # 添加日志
    def add_log(self,text):
        log_text = ''
        if text != '':
            log_text = "%s %s" % (time.strftime("%H:%M", time.localtime()),text)
        self.log_list.InsertItems([log_text],0)

    # 保持运行检查未完成任务
    def check_task_win(self):
        # print('running_index',self.running_index)
        while True:
            print('yes')
            time.sleep(5)

app = wx.App()
frame = Ep(None)
ready = frame.start()
if ready == False:
    sys.exit()

frame.Show(False)
app.MainLoop()