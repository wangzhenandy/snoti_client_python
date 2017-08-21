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
    pass

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
    pass

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