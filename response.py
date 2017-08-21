#! python3
# -*- coding: utf-8 -*-
import json
import client

class Response:
    def __init__(self, data):
        self.resp_data = json.loads(data)
        self.__create_handler()

    # 新增的事件通知，需要加到如下字典中，并对应实现一个子类
    def __create_handler(self):
        self.__cmd_handler = {
            'login_res': LoginRes,
            'pong': PongRes,
            'remote_control_res': ControlRes,
            'event_push': EventPush
        }
        self.event_handler = {
            'datapoints_changed': EventDpChanged,
            'device_online': EventDevOnline,
            'device_offline': EventDevOffline,
            'attr_alert': EventAlertFault,
            'attr_fault': EventAlertFault,
            'device_status_raw': EventDevRaw,
            'device_status_kv': EventDevKv,
            'sub_device_added': EventSubDevAdd,   
            'sub_device_deleted': EventSubDevDel
        }

    def handle(self, clientItem):
        cmd = self.resp_data.pop('cmd')
        if cmd in self.__cmd_handler.keys():
            return self.__cmd_handler[cmd].handle(self, clientItem)
        return None, None

    def run_callback(self, fun, data):
        try:
            fun(data)
        finally:
            pass

# 请求响应与事件回调子类

class LoginRes(Response):
    def handle(self, *): 
        if self.resp_data['data']['result']:
            return "login_success", None
        return "login_fault", None

class PongRes(Response):
    def handle(self, *):
        print('pong')
        return None, None

class ControlRes(Response):
    def handle(self, *):
        print(json.dumps(self.resp_data))
        return None, None

class EventPush(Response):
    def handle(self, clientItem):
        event_type = self.resp_data.pop('event_type')
        self.delivery_id = self.resp_data.pop('delivery_id')
        if event_type in self.event_handler.keys():
            return self.event_handler[event_type].handle(self, clientItem)
        return "ack", self.delivery_id

class EventDpChanged(EventPush):
    def handle(self, *):
        return "ack", self.delivery_id

class EventDevOnline(EventPush):
    def handle(self, client clientItem):
        self.resp_data['online_type'] = 'online'
        self.run_callback(clientItem.callback.event_dev_online_offline, self.resp_data)
        return "ack", self.delivery_id

class EventDevOffline(EventPush):
    def handle(self):
        self.resp_data['online_type'] = 'offline'
        self.run_callback(callback.event_dev_online_offline, self.resp_data)
        return "ack", self.delivery_id

class EventAlertFault(EventPush):
    def handle(self):
        pass

class EventDevRaw(EventPush):
    def handle(self):
        self.run_callback(callback.event_dev_status_raw, self.resp_data)
        return "ack", self.delivery_id

class EventDevKv(EventPush):
    def handle(self):
        self.run_callback(callback.event_dev_status_kv, self.resp_data)
        return "ack", self.delivery_id

class EventSubDevAdd(EventPush):
    def handle(self):
        pass

class EventSubDevDel(EventPush):
    def handle(self):
        pass

if __name__ == '__main__':
    a = Response('{"cmd" : "pong"}')
    a.handle()