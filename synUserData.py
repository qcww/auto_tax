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
    # post = ("44","公司","91340100094822207C","wcy123456","2019-01-01","2019-01-30","5")
    # post = ("4279","安徽宝甲环保建材有限公司","91340104MA2RTQ7T63","wcy123456","2020-06-01","2020-06-06","9")
    # post = ("54","安徽宝甲环保建材有限公司","91340104MA2RHE9X3A","zyj123456","2020-06-01","2020-06-06","7")
    # post = ("306","余额不足测试","91340104MA2RNYJX4T","wcy123456","2020-06-01","2020-06-06","7")
    # post = ("335","社保未扣问题","9134010039464211X8","wcy123456","2020-06-01","2020-06-06","7")
    # post = ("1335","合肥知时文化传媒有限公司","91340100MA2MRDEL43","zs123456","2020-06-01","2020-06-06","7")
    # post = ("1335","安徽良哥通信服务有限公司","91340104MA2RNYJX4T","wcy123456","2020-06-01","2020-06-06","7")
    # post = ("350","合肥鲜又惠农业科技有限公司","91340104MA2TPHQJ0H","wcy123456","2020-06-01","2020-06-06","7")
    # post = ("2832","安徽百口汇食品有限公司","91340100MA2NMY1Q3Q","wcy123456","2020-05-01","2020-06-06","10")
    # post = ("1428","合肥徽聚元科技有限公司","91340100MA2N00MQ42","wcy123456","2020-06-01","2020-06-06","9")
    # post = ("294","合肥亘恒房地产销售代理有限公司","91340111MA2NKH6L7X","wcy123456","2020-06-01","2020-06-06","9")
    post = ("294","安徽数智人工智能科技有限公司","91340100MA2TCNUG7B","wcy123456","2020-06-01","2020-06-06","9")
    post_data = '||'.join(post)

    ws.send('{"type":"action","reply":"1","room_id":"%s","data":"%s","client_name":"tax_ah4"}' % (room_id,post_data))

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

ws.run_forever()