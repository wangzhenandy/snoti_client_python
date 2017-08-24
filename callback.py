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