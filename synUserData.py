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
    # post = ("5320","安徽泽伊度企业管理有限公司 ","91340111MA2RXPQH8L","wcy123456","202001","202007","10")
    # post = ("7059","合肥瑞扬建筑工程有限公司 ","91340102MA2TMAAN6R","wcy123456","202001","202007","10")
    # post = ("410","合肥易佳装饰设计工程有限公司 ","91340100348702644C","","202001","202007","11")
    # post = ("64","安徽百胜医疗管理有限公司 ","91340100355192208K","","202001","202007","11")
    # post = ("4022","合肥平福祥餐饮管理有限公司 ","91340104MA2RB5TT0Y","wcy123456","202001","202007","12")
    # post = ("7690","合肥乐智商务服务有限公司 ","18226208933","lz123456","202001","202007","12")
    # post = ("6240","安徽衍诺照明科技有限公司 ","18326192008","2525775wtos8","202001","202007","12")
    # post = ("6463","合肥优职优才企业信息咨询有限公司","91340102MA2TEPFH6Q","yz123456","202001","202007","12")
    # post = ("7407","安徽伍贰捌房地产营销策划有限公司","91340111MA2TRT4GXC","wcy123456","202001","202007","12")
    post = ("2336","合肥市柳成新材料有限公司","91340100MA2RB6CQ0T","lc123456","202001","202007","9")
    # 7674||安徽宜家装饰工程有限公司||91340111MA2TWH630N||zj820309||||||7
    # post = ("6463","合肥优职优才企业信息咨询有限公司","91340102MA2TEPFH6Q","yz123456","202001","202007","12")
    post_data = '||'.join(post)

    ws.send('{"type":"action","reply":"1","room_id":"%s","data":"%s","client_name":"tax_ah4"}' % (room_id,post_data))

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

ws.run_forever()