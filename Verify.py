#coding=utf-8

import os
import time
import math

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from HTool import HTool
import pyautogui

class XnwVerify:
    def verify_image(self,driver):
        # # 打开登录页面
        # self.driver.get('https://www.nuocity.com/xnw_user_ssoservice/login')
        # time.sleep(2)
        # self.driver.execute_script("$('.tab li:eq(1)').click()")
        self.driver = driver
        # 获取鼠标位置
        bar_element = self.driver.find_element_by_id('verify-move-block')
        # 鼠标移至指定位置
        # a = m.position()    #获取当前坐标的位置
        start_x = bar_element.location['x'] + 20
        stary_y = bar_element.location['y'] + 90
        # m.move(start_x, stary_y)   #鼠标移动到(x,y)位置
        pyautogui.moveTo(x=start_x, y=stary_y)

        # timestrmap = time.strftime('%Y%m%d_%H.%M.%S')
        # imgPath = os.path.join('./', '%s.png' % str(timestrmap))

        # self.driver.save_screenshot(imgPath)
        # print('screenshot:', timestrmap, '.png')
        time.sleep(2)
        pic_element = self.driver.find_element_by_id('verify-img-out')
        # left = pic_element.location['x']
        # top = pic_element.location['y']

        # location_x = left + pic_element.size['width'] - 20
        # location_y = top + 90
        # for _ in range(50):
        #     self.get_element_image(pic_element)
        #     m.click(location_x,location_y)
        #     time.sleep(0.3)
        target_img = self.get_element_image(pic_element)
        match_res = self.try_match_img(target_img)
        # print('最终匹配',match_res)
        fix_pixel = self.fix_img(target_img,match_res)
        # print('fix_pixel',fix_pixel)
        
        pyautogui.mouseDown()
        pyautogui.dragRel(xOffset=fix_pixel,yOffset=0,duration=1,button='left',mouseDownUp=False)
        pyautogui.mouseUp()

    """
    截图,指定元素图片
    :param element: 元素对象
    :return: 无
    """
    """图片路径"""
    def get_element_image(self,element):
        timestrmap = time.strftime('%Y%m%d_%H.%M.%S')
        imgPath = os.path.join('./', '%s.png' % str(timestrmap))

        """截图，获取元素坐标"""
        self.driver.save_screenshot(imgPath)
        left = element.location['x']
        top = element.location['y']
        elementWidth = left + element.size['width']
        elementHeight = top + element.size['height']

        picture = Image.open(imgPath)
        picture = picture.crop((left, top, elementWidth, elementHeight))
        timestrmap = time.strftime('%Y%m%d-%H-%M-%S')
        newPath = os.path.join('./', '%s.png' % str(timestrmap))
        picture.save(newPath)
        print('screenshot:', timestrmap, '.png')
        try:
            os.remove(imgPath)
        except(FileNotFoundError):
            print("文件不存在")
        return newPath

    #打开浏览器
    def open_browser(self):
        chrome_options = Options()
        #修改windows.navigator.webdriver，防机器人识别机制，selenium自动登陆判别机制
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 使用代理
        # chrome_options.add_argument("--proxy-server=http://125.123.18.114:4226")
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()


    # 将图片转化为RGB
    def make_regalur_image(self,img, size=(64, 64)):
        gray_image = img.resize(size).convert('RGB')
        return gray_image
    
    # 计算直方图
    def hist_similar(self,lh, rh):
        assert len(lh) == len(rh)
        hist = sum(1 - (0 if l == r else float(abs(l-r))/max(l,r))for l, r in zip(lh, rh))/len(lh)
        return hist
    
    # 计算相似度
    def calc_similar(self,li, ri):
        calc_sim = self.hist_similar(li.histogram(), ri.histogram())
        return calc_sim

    # 尝试匹配
    def try_match_img(self,match_img):
        image1 = Image.open(match_img)
        image1 = self.make_regalur_image(image1)
        match_max = 0
        match_index = 0
        for i in range(19):
            image2 = Image.open("./verify_match/xnw/%s.png" % str(i+1))
            image2 = self.make_regalur_image(image2)
            match_val = self.calc_similar(image1, image2)
            # print(i,match_val)
            if match_val > match_max:
                match_max = match_val
                match_index = i
        return match_index + 1 

    def fix_img(self,img_path,match_index):
        pre_img = Image.open("./verify_match/xnw/%s.png" % str(match_index))
        pre_pixels = pre_img.load()

        img = Image.open(img_path)
        pixels = img.load()
        l_max = 0
        r_max = 0

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if i >= img.size[0]*0.92 or j > img.size[1]*0.92 or j < img.size[1]*0.1:
                    pixels[i,j] = (255, 255, 255)
                    continue
                if pixels[i,j][0] + pixels[i,j][1] + pixels[i,j][2] - pre_pixels[i,j][0] - pre_pixels[i,j][1] - pre_pixels[i,j][2] >20:
                    # pixels[i,j] = (0, 0, 0)
                    if i > img.size[0]/3 and r_max < i:
                        r_max = i
                    elif i < img.size[0]/3 and l_max < i:
                        l_max = i
                    pixels[i,j] = (0, 0, 0)
                else:
                    pixels[i,j] = (255, 255, 255) 
        try:
            os.remove(img_path)
        except(FileNotFoundError):
            print("文件不存在")
        # img.save('xinireila.png')    
        return r_max - l_max

class HfSwVerify:
    def __init__(self,driver):
        self.driver = driver

    def verify_image(self):
        driver = self.driver

        #点击登录
        driver.execute_script("com.login('fm3',true)")
        self.match_action()

        # m.press(start_x,stary_y)
        # for i in range(10):
        #     m.move(start_x + i*20,stary_y)
        #     time.sleep(3)
        # m.release(start_x + fix_pixel,stary_y)


    """
    截图,指定元素图片
    :param element: 元素对象
    :return: 无
    """
    """图片路径"""
    def get_element_image(self,element):
        timestrmap = time.strftime('%Y%m%d_%H.%M.%S')
        imgPath = os.path.join('./', '%s.png' % str(timestrmap))

        """截图，获取元素坐标"""
        self.driver.save_screenshot(imgPath)
        left = element.location['x']
        top = element.location['y']
        elementWidth = left + element.size['width']
        elementHeight = top + element.size['height']

        picture = Image.open(imgPath)
        picture = picture.crop((left, top, elementWidth, elementHeight))
        timestrmap = time.strftime('%Y%m%d-%H-%M-%S')
        newPath = os.path.join('./', '%s.png' % str(timestrmap))
        picture.save(newPath)
        # print('screenshot:', timestrmap, '.png')
        try:
            os.remove(imgPath)
        except(FileNotFoundError):
            print("文件不存在")
        return newPath

    #打开浏览器
    def open_browser(self):
        chrome_options = Options()
        #修改windows.navigator.webdriver，防机器人识别机制，selenium自动登陆判别机制
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 使用代理
        # chrome_options.add_argument("--proxy-server=http://125.123.18.114:4226")
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        # # 打开登录页面
        self.driver.get('https://etax.anhui.chinatax.gov.cn/cas/login')
        time.sleep(2)
        #打开登录框
        Action = ActionChains(self.driver)# 实例化一个action对象
        login_open = self.driver.find_element_by_id("login")#获取打开登录框的按钮
        login_open_click = Action.click(login_open)#点击
        login_open_click.perform()
        time.sleep(1)
        # driver.execute_script('init.openLoginView()')
        tax_code_input = self.driver.find_element_by_id("username")
        pwd_input = self.driver.find_element_by_id("password")
        tax_code_input.send_keys('913401000875815800')
        pwd_input.send_keys('wcy123456')
        time.sleep(1)

    # 将图片转化为RGB
    def make_regalur_image(self,img, size=(64, 64)):
        gray_image = img.resize(size).convert('RGB')
        return gray_image
    
    # 计算直方图
    def hist_similar(self,lh, rh):
        assert len(lh) == len(rh)
        hist = sum(1 - (0 if l == r else float(abs(l-r))/max(l,r))for l, r in zip(lh, rh))/len(lh)
        return hist
    
    # 计算相似度
    def calc_similar(self,li, ri):
        calc_sim = self.hist_similar(li.histogram(), ri.histogram())
        return calc_sim

    # 尝试匹配去噪点
    def try_match_img(self,match_img):
        image1 = Image.open(match_img)
        image1 = self.make_regalur_image(image1)
        match_max = 0
        match_index = 0
        for i in range(99):
            image2 = Image.open("./verify_match/hf_swj/%s.png" % str(i+1))
            image2 = self.make_regalur_image(image2)
            match_val = self.calc_similar(image1, image2)
            # print(i,match_val)
            if match_val > match_max:
                match_max = match_val
                match_index = i
        return match_index + 1

    def check_pixels(self,pixels,i,j,color):
        for st in range(5):
            st += 1
            if (pixels[i+st,j] == color and pixels[i-st,j] == color):
                return True
        for st in range(5):
            st += 1
            if (pixels[i,j+st] == color and pixels[i,j-st] == color):
                return True
        return False        

    def match_action(self):
        time.sleep(2)
        # 获取鼠标位置
        bar_element = self.driver.find_element_by_class_name('captcha_slider_bar')
        # 鼠标移至指定位置
        # a = m.position()    #获取当前坐标的位置
        start_x = bar_element.location['x'] + 20
        stary_y = bar_element.location['y'] + 90
        # m.move(start_x, stary_y)   #鼠标移动到(x,y)位置
        pyautogui.moveTo(x=start_x, y=stary_y)

        time.sleep(1)
        pic_element = self.driver.find_element_by_class_name('captcha_slider_image_area')
        # left = pic_element.location['x']
        # top = pic_element.location['y']

        # location_x = left + pic_element.size['width'] - 20
        # location_y = top + 90
        # for _ in range(450):
        #     self.driver.execute_script("$('.captcha_slider_image_slider').remove()")
        #     self.get_element_image(pic_element)
        #     pyautogui.click(location_x,location_y)
        #     time.sleep(5)
        # time.sleep(500)    
        img_path = self.get_element_image(pic_element)
        match_index = self.try_match_img(img_path)
        # print('最终匹配',match_index)
        pre_img = Image.open("./verify_match/hf_swj/%s.png" % str(match_index))
        pre_pixels = pre_img.load()

        img = Image.open(img_path)
        pixels = img.load()
        l_max = 0
        r_max = 0
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # print(pixels[i,j][0] , pre_pixels[i,j][0])
                if pixels[i,j][0] + pixels[i,j][1] + pixels[i,j][2] - pre_pixels[i,j][0] - pre_pixels[i,j][1] - pre_pixels[i,j][2] >20:
                    pixels[i,j] = (0, 0, 0)
                    
                    if i > img.size[0]/3 and r_max < i:
                        r_max = i
                    elif i < img.size[0]/3 and l_max < i:
                        l_max = i
                else:
                    pixels[i,j] = (255, 255, 255)
     
        first_point = [0,0]
        height_max = 0
        # 二次降噪处理
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if i < img.size[0]/7 or i > img.size[0]*0.9:
                    # 第一个像素点
                    if pixels[i,j] == (0, 0, 0, 255):
                        if first_point == [0,0]:
                            first_point = [i,j]
                        if j > height_max:
                            height_max = j
                else:
                    if pixels[i,j] == (0, 0, 0, 255) and self.check_pixels(pixels,i,j,(255, 255, 255, 255)) == True:
                        pixels[i,j] = (255, 255, 255)
        # print('first_point',first_point)
        pic_width = 49
        # print('height_max',height_max)
        # print('width',pic_width)

        # 计算距离
        match_max_x = 0
        for i in range(img.size[0]):
            start_x = i + pic_width
            start_y = first_point[1] + 25
            if start_x >= img.size[0]:
                break
            if pixels[start_x,start_y] == (0, 0, 0, 255) and pixels[start_x+3,start_y+3] != (0, 0, 0, 255) and pixels[start_x+3,start_y-3] != (0, 0, 0, 255) and start_x > match_max_x:
                match_max_x = start_x

        for r in range(img.size[1]):
            pixels[match_max_x - pic_width + 2,r] = (255, 0, 0)
            pixels[match_max_x,r] = (255, 0, 0)
        # img.save(img_path)
        try:
            os.remove(img_path)
        except(FileNotFoundError):
            print("文件不存在")
        # 调整距离
        end_fix = round((match_max_x - 220) * 0.07)

        pyautogui.mouseDown()
        pyautogui.dragRel(xOffset=match_max_x - pic_width + 2 + end_fix,yOffset=0,duration=1,button='left',mouseDownUp=False)
        pyautogui.mouseUp()
        # print('match_max_x',match_max_x)
        # print('end_fix',end_fix)
        # time.sleep(80000)
        try:
            pass_err = self.driver.find_element_by_id("captcha")
            if pass_err:
                print('验证码失败，重试')
                htool = HTool()
                htool.set_config('login','last_run_time',round(time.time()))
                return self.match_action()
        except:
            pass
        