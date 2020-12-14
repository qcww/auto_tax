#coding=utf-8

import websocket
import json

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    # room_id = "sys_tax_group"
    room_id = "0da851c3bb31aaf458919479dcb726f0"
    ws.send('{"type":"login","room_id":%s,"client_name":"%s"}' % (room_id,'tax_ah4'))
    # post = ("759","安徽微梦文化传媒有限公司","91340100MA2MTF1W84","wcy123456","","","9")
    # post = ("6099","安徽并育文化科技有限公司","91340102MA2RTN5Y6G","HONGwei1","","","")
    # post_data = '||'.join(post)
    post_data = '3233||安徽荆竹科技有限公司||91340104MA2TPJ0U0R||wcy123456||2020-12-01||2020-12-12||8'
    # post_data = '1280||合肥斯威迈船舶科技有限公司||91340100MA2MX8K0X3||wcy123456||||||9'
    # post_data = '13||合肥医健电子科技有限公司||91340100358014204P||wcy123456||2020-08-01||2020-12-12||8'
    # post_data = '6129||安徽嘉信企业管理咨询有限公||91340104MA2T9JNP92||wcy123456||||||9'
    # post_data = '7920||安徽天星装饰安装工程有限公司||9134010057706472XY||tx123456||||||7'
    # post_data = '7579||安徽岂月环境科技有限公司||91340121MA2TUBFP0T||qy123456||||||9'
    ws.send('{"type":"action","reply":"1","room_id":"%s","data":"%s","client_name":"tax_ah4"}' % (room_id,post_data))

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

ws.run_forever()