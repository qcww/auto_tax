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
    ws.send('{"type":"login","room_id":"0da851c3bb31aaf458919479dcb726f0","client_name":"%s"}' % 'tax_ah4')
    post = ("44","公司","91340100094822207C","wcy123456","2019-01-01","2019-01-30","5")
    post_data = '||'.join(post)
    ws.send('{"type":"action","reply":"1","room_id":"0da851c3bb31aaf458919479dcb726f0","data":"%s","client_name":"tax_ah4"}' % post_data)

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://im.itking.cc:12366",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

ws.run_forever()