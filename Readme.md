snoti client
=======
v1.0.0

## Prerequisites
* [Python 3](https://www.python.org/)

## 使用说明
* 用户需要参考callback.py文件中的函数结构，实现一个自定义的callback模块，每个函数的参数格式和使用场景，请参考文件中的注释。
* 接口说明：
```

# 实例化一个client对象
# 参数说明：
#     product_key：是产品标识，见开发者中心的产品信息
#     auth_id, auth_secret：为SNoti登录鉴权参数，通过开发者中心开通SNoti服务后，创建生成一对参数
#     callback，用户回调模块名称
#     可选参数有：subkey：用于数据副本功能，默认可不填，events：订阅的设备事件类型，默认全量订阅
client = Client("c74fd6e832eb42de80540d7d738fe025", "9UDAyB8pQY6w2HSewJmwvw", "r5A9PhsYQIGhJ03SSOsIqQ", subkey="sandbox_000", callback = callback)

# 客户端连接SNoti服务
# 可选参数有：snoti_host， snoti_port，可指定连接SNoti服务的域名和端口
# 连接成功后，客户端封装了自动登录，心跳，出错重连，接收消息等功能
# 用户只需要在回调函数中，关心每种回调的业务逻辑即可
client.connect()

# 控制设备接口（数据点协议）
# 参数说明：
#     did: 设备标识
#     mac: 设备mac地址
#     attrs: 控制指令，具体为指定数据点数据，数据类型为dict
#            其中，布尔类型数据点的取值为True | False；
#                 uint类型数据点的取值为int；
#                 枚举类型数据点的取值为枚举显示值字符串，可支持utf8格式的中文；
#                 扩展类型数据点的取值为十进制的byte数组，例如[0,1,255]，数组长度必须等于数据点定义的长度，不足长度的，后面补0
#     可选参数有：msg_id：控制指令标识，用于对应控制响应事件中的msg_id，参数类型可以为数字或字符串
client.control_kv("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", {"number":5, "bool": True, "enum": '红色'})

# 控制设备接口（自定义协议）
# 参数说明：
#     did: 设备标识
#     mac: 设备mac地址
#     data: 控制指令，数据类型为Hex字符串，例如：'0011FF'
client.control_raw("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", '0011FF')

# 断开与SNoti服务的连接
client.disconnect()

```
**特别注意：控制的设备，必须属于客户端实例化时指定的产品(product_key)，并且did和mac必须是合法的，对应的。**

* 使用例子：

```
#socket_cli.py
#! python3
# -*- coding: utf-8 -*-
from snoti_client_python.client import Client
import user_callback

if __name__ == '__main__':
    product_key = "c74fd6e832eb42de80540d7d738fe025"
    auth_id = "9UDAyB8pQY6w2HSewJmwvw"
    auth_secret = "r5A9PhsYQIGhJ03SSOsIqQ"
    subkey = "sandbox_000"
    c = Client(product_key, auth_id, auth_secret, subkey="sandbox_000", callback=user_callback)
    c.connect()
    while True: pass

```
```
#user_callback.py
#! python3
# -*- coding: utf-8 -*-
import json

'''
data = {
    "error_code": <int>
    "msg": <str>
}
'''
def event_error(data):
    errcode = data['error_code']
    msg = data['msg']
    print('error: %s, %s' % (errcode, msg))

'''
data = {
    "product_key": <str>,
    "did": <str>,
    "mac": <str>,
    "online_type": "online" | "offline",
    "created_at": <float>
}
'''
def event_dev_online_offline(data):
    did = data['did']
    mac = data['mac']
    online_type = data['online_type']
    print('device %s: %s, %s' % (online_type, did, mac))

'''
data = {
    "product_key": <str>,
    "did": <str>,
    "mac": <str>,
    "data": <base64 str>,
    "created_at": <float>
}
'''
def event_dev_status_raw(data):
    pass

'''
data = {
    "product_key": <str>,
    "did": <str>,
    "mac": <str>,
    "data":
    {
        <key> : <value>,
        ...
    },
    "created_at": <float>
}
其中，数据点kv的取值类型为：
布尔类型，警告类型，故障类型的数据点，取值为0或1，0代表False，1代表True
枚举类型的数据点，取值为数据点定义的枚举显示字符串，如遇中文，则使用unicode编码表示
uint类型的数据点，取值为整数
扩展类型的数据点，取值为hex字符串
例如：{"binary": "0001ff0000", "bool1": 1, "enum": "\u7ea2\u8272", "number": 1, "alert": 0, "bool": 0}
'''
def event_dev_status_kv(data):
    did = data['did']
    mac = data['mac']
    kv = data['data']
    print('device kv: %s, %s: %s' % (did, mac, json.dumps(kv)))

'''
data = {
    "product_key": <str>,
    "created_at": <float>
}
'''
def event_dev_datapoint_changed(data):
    pass

'''
data = {
    "product_key": <str>,
    "did": <str>,
    "mac": <str>,
    "child_product_key": <str>,
    "child_did": <str>,
    "child_mac": <str>,
    "created_at": <float>
}
'''
def event_sub_dev_added(data):
    pass

'''
data = {
    "product_key": <str>,
    "did": <str>,
    "mac": <str>,
    "child_did": <str>,
    "child_mac": <str>,
    "created_at": <float>
}
'''
def event_sub_dev_deleted(data):
    pass


if __name__ == '__main__':
    pass
```

## Change log: v1.0.0 (2017/08)
* First version

