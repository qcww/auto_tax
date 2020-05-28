#coding=utf-8

import json
from urllib.parse import urlparse

cc = 'sfxyh=&djxh=10113401010000167286&zgswjgDm=13401030000&gdslx=1&sbjklb=0&btSelectItem=on&btSelectItem=on&btSelectItem=on&yzpzxh=10013420000039073311&ybtse=327.46&znjLrExt=0.0&zsuuid=C8FD4D5BEB2B6F0DC0CDEB77EF1AF01E&yzpzmxxh=2&yzpzzlDm=BDA0610678&skssswjg=13401030000&skssqq=2020-04-01&skssqz=2020-04-30&yzpzxh=10013420000039073311&ybtse=491.19&znjLrExt=0.0&zsuuid=A6149FDDB1330D4887D4D51236599D61&yzpzmxxh=1&yzpzzlDm=BDA0610678&skssswjg=13401030000&skssqq=2020-04-01&skssqz=2020-04-30&yzpzxh=10013420000039073311&ybtse=1146.11&znjLrExt=3.44&zsuuid=D76757E29924A60004D7E0A1F84C9569&yzpzmxxh=3&yzpzzlDm=BDA0610678&skssswjg=13401030000&skssqq=2020-04-01&skssqz=2020-04-30'
parse = {}
js_arr = cc.split('&')
for i in js_arr:
    sp_arr = i.split('=')
    parse[sp_arr[0]] = sp_arr[1]

print(parse)