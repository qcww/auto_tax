import win32con
import win32api
import winreg
import os
import time
import sys
import uuid

def get_auto_path():
    try:
        reg_key = winreg .OpenKey(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Run')
        app_path, _ = winreg.QueryValueEx(reg_key, "AutoTax")
    except:
        app_path = ''

    return app_path

def add_auto_run(path_file):
    name = 'AutoTax'      # 获得文件名的前部分,如：newsxiao
    if os.path.exists(path_file.split(' ')[0]) == False:
        return False
    # 防止重复设置
    auto_path = get_auto_path()
    if auto_path != '':
        if path_file == auto_path:
            print('阻拦重复设置')
            return False


    KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    # 异常处理
    try:
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,  KeyName, 0,  win32con.KEY_ALL_ACCESS)
        win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, path_file)
        win32api.RegCloseKey(key)
    except:
        return False
    return True

# add_auto_run("D:\\phpstudy\\PHPTutorial\\WWW\\auto_export\\main.exe /background")

def set_client_path():
    reg_root = win32con.HKEY_LOCAL_MACHINE
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AutoTax.exe"
    reg_flags = win32con.WRITE_OWNER|win32con.KEY_WOW64_64KEY|win32con.KEY_ALL_ACCESS

    config_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    client_path = get_client_path()
    if str(client_path) != '' and str(client_path) == str(config_path):
        print('阻拦重复设置')
        return True

    try:
        #直接创建（若存在，则为获取）
        key, _ = win32api.RegCreateKeyEx(reg_root, reg_path, reg_flags)

        #设置项
        
        print('设置路径',config_path)
        win32api.RegSetValueEx(key, "Path", 0, win32con.REG_SZ, config_path)

        #关闭
        win32api.RegCloseKey(key)
        return True
    except:
        return False

def get_client_path():
    try:
        reg_key = winreg .OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AutoTax.exe")
        app_path, _ = winreg.QueryValueEx(reg_key, "Path")
    except:
        app_path = ''

    return app_path

def get_pc_id():
    try:
        reg_key = winreg .OpenKey(winreg .HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AutoTax.exe")
        uid, _ = winreg.QueryValueEx(reg_key, "uid")
        first = False
    except:
        uid = set_pc_id()
        first = True

    return uid,first

def set_pc_id():
    reg_root = win32con.HKEY_LOCAL_MACHINE
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AutoTax.exe"
    reg_flags = win32con.WRITE_OWNER|win32con.KEY_WOW64_64KEY|win32con.KEY_ALL_ACCESS

    try:
        #直接创建（若存在，则为获取）
        key, _ = win32api.RegCreateKeyEx(reg_root, reg_path, reg_flags)
        #设置项
        uid = uuid.uuid1()
        win32api.RegSetValueEx(key, "uid", 0, win32con.REG_SZ, str(uid))

        #关闭
        win32api.RegCloseKey(key)
        return uid
    except:
        return ''



def get_app_path(app_path,app_name):
    app_path = app_path
    if app_path == "":
        try:
            reg_key = winreg .OpenKey(winreg .HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\fwkp.exe")
            app_path_all, _ = winreg.QueryValueEx(reg_key, "Path")

            path_start = app_path_all.find('开票软件')
            app_path = app_path_all[0:int(path_start)+5] + app_name
        except:
            app_path = ''
    else:
        app_path = app_path + app_name
    if app_path != '' and os.path.exists(app_path):
        return app_path
    return ''

def get_credit_code():
    try:
        reg_key = winreg .OpenKey(winreg .HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\fwkp.exe")
        list_key = winreg.QueryInfoKey(reg_key)
        if(list_key):
            for i in range(int(list_key[0])):
                user = winreg.EnumKey(reg_key,i)
                print(user.split('.')[0])
        # return list_key[0]
        return ''

    except:
        credit_code = ''
    return credit_code    
