#! python3
# -*- coding: utf-8 -*-
import json

class Request:
    def __init__(self, cmd):
        self._cmd = cmd
        self.req_data = {"cmd": self._cmd}

    def build_json(self):
        return json.dumps(self.req_data) + '\n'

class LoginReq(Request):
    def __init__(self, prefetch_count = 50):
        self._cmd = 'login_req'
        self._prefetch_count = prefetch_count
        self._data = []
        self.req_data = ''

    def add_login_data(self, product_key, auth_id, auth_secret, subkey, events):
        data = {
            'product_key': product_key,
            'auth_id': auth_id,
            'auth_secret': auth_secret,
            'subkey': subkey,
            'events': events
        }
        self._data.append(data)

    def build_json(self):
        self.req_data = {
            'cmd': self._cmd,
            'prefetch_count': self._prefetch_count,
            'data': self._data
        }
        return Request.build_json(self)

class AckReq(Request):
    def __init__(self, delivery_id):
        self._cmd = 'event_ack'
        self._delivery_id = delivery_id

    def build_json(self):
        self.req_data = {
            'cmd': self._cmd,
            'delivery_id': self._delivery_id
        }
        return Request.build_json(self)

class ControlReq(Request):
    def __init__(self, msg_id=None):
        self._cmd = 'remote_control_req'
        self._msg_id = msg_id
        self._data = []

    def add_control_raw(self, cmd, did, mac, product_key, raw):
        data = {
            'cmd': cmd,
            'data': {
                'did': did,
                'mac': mac,
                'product_key': product_key,
                'raw': raw
            }
        }
        self._data.append(data)
    
    def add_control_kv(self, cmd, did, mac, product_key, attrs):
        data = {
            'cmd': cmd,
            'data': {
                'did': did,
                'mac': mac,
                'product_key': product_key,
                'attrs': attrs
            }
        }
        self._data.append(data)

    def build_json(self):
        self.req_data = {
            'cmd': self._cmd,
            'msg_id': self._msg_id,
            'data': self._data
        }
        return Request.build_json(self)

if __name__ == '__main__':
    test_req = Request('ping')
    print(test_req.build_json())