#! python3
# -*- coding: utf-8 -*-
import json

class Request:
    def __init__(self, cmd):
        self.__cmd = cmd
        self.req_data = {"cmd": self.__cmd}

    def build_json(self):
        return json.dumps(self.req_data) + '\n'
    
    # def __str__(self):
    #     return json.dumps(self.req_data) + '\n'

    # def __repr__(self):
    #     return self.__str__()

class LoginReq(Request):
    def __init__(self, prefetch_count = 50):
        self.__cmd = 'login_req'
        self.__prefetch_count = prefetch_count
        self.__data = []
        self.req_data = ''

    def add_login_data(self, product_key, auth_id, auth_secret, subkey, events):
        data = {
            'product_key': product_key,
            'auth_id': auth_id,
            'auth_secret': auth_secret,
            'subkey': subkey,
            'events': events
        }
        self.__data.append(data)

    def build_json(self):
        self.req_data = {
            'cmd': self.__cmd,
            'prefetch_count': self.__prefetch_count,
            'data': self.__data
        }
        return Request.build_json(self)

class AckReq(Request):
    def __init__(self, delivery_id):
        self.__cmd = 'event_ack'
        self.__delivery_id = delivery_id

    def build_json(self):
        self.req_data = {
            'cmd': self.__cmd,
            'delivery_id': self.__delivery_id
        }
        return Request.build_json(self)

class ControlReq(Request):
    def __init__(self, msg_id=None):
        self.__cmd = 'remote_control_req'
        self.__msg_id = msg_id
        self.__data = []

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
        self.__data.append(data)
    
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
        self.__data.append(data)

    def build_json(self):
        self.req_data = {
            'cmd': self.__cmd,
            'msg_id': self.__msg_id,
            'data': self.__data
        }
        return Request.build_json(self)

if __name__ == '__main__':
    test_req = Request('ping')
    print(test_req)
    print(test_req.__repr__())
    test_req.build_json()
    print(test_req)
    print(test_req.__repr__())
