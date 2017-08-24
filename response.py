#! python3
# -*- coding: utf-8 -*-
import json
from .settings import LOGGING_CONFIG

# logging
import logging
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger('client')

class Response:
    def __init__(self, data):
        self.resp_data = json.loads(data, encoding='utf-8')
        self._create_handler()

    # 新增的事件通知，需要加到如下字典中，并对应实现一个子类
    def _create_handler(self):
        self._cmd_handler = {
            'login_res': LoginRes,
            'pong': PongRes,
            'remote_control_res': ControlRes,
            'event_push': EventPush,
            'invalid_msg': InvalidRes
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

    def handle(self, callback):
        cmd = self.resp_data.pop('cmd')
        if cmd in self._cmd_handler.keys():
            return self._cmd_handler[cmd].handle(self, callback)
        return None, None

    def run_callback(self, module, funcname, data):
        try:
            func = getattr(module, funcname)
            func(data)
        except AttributeError:
            logger.warn("用户回调函数 %s 没有被定义" % (funcname))
        except Exception as e:
            logger.warn("用户回调函数 %s 运行失败: %s" % (funcname, e))
        finally:
            pass

# 请求响应与事件回调子类

class LoginRes(Response):
    def handle(self, *args): 
        if self.resp_data['data']['result']:
            return "login_success", self.resp_data['data']['msg']
        return "login_fault", self.resp_data['data']['msg']

class PongRes(Response):
    def handle(self, *args):
        return "pong", None

class ControlRes(Response):
    def handle(self, *args):
        logger.debug(json.dumps(self.resp_data))
        return None, None

class InvalidRes(Response):
    def handle(self, callback):
        errcode = self.resp_data['error_code']
        if errcode in [4001, 4003]:
            return 'not_login', self.resp_data['msg']
        if errcode == 4009:
            return 'has_login', self.resp_data['msg']
        self.run_callback(callback, 'event_error', self.resp_data)
        return None, None

class EventPush(Response):
    def handle(self, callback):
        event_type = self.resp_data.pop('event_type')
        self.delivery_id = self.resp_data.pop('delivery_id')
        if event_type in self.event_handler.keys():
            return self.event_handler[event_type].handle(self, callback)
        return "ack", self.delivery_id

class EventDpChanged(EventPush):
    def handle(self, *args):
        return "ack", self.delivery_id

class EventDevOnline(EventPush):
    def handle(self, callback):
        self.resp_data['online_type'] = 'online'
        self.run_callback(callback, 'event_dev_online_offline', self.resp_data)
        return "ack", self.delivery_id

class EventDevOffline(EventPush):
    def handle(self, callback):
        self.resp_data['online_type'] = 'offline'
        self.run_callback(callback, 'event_dev_online_offline', self.resp_data)
        return "ack", self.delivery_id

class EventAlertFault(EventPush):
    def handle(self, *args):
        return "ack", self.delivery_id

class EventDevRaw(EventPush):
    def handle(self, callback):
        self.run_callback(callback, 'event_dev_status_raw', self.resp_data)
        return "ack", self.delivery_id

class EventDevKv(EventPush):
    def handle(self, callback):
        self.run_callback(callback, 'event_dev_status_kv', self.resp_data)
        return "ack", self.delivery_id

class EventSubDevAdd(EventPush):
    def handle(self, *args):
        self.run_callback(callback, 'event_sub_dev_added', self.resp_data)
        return "ack", self.delivery_id

class EventSubDevDel(EventPush):
    def handle(self, *args):
        self.run_callback(callback, 'event_sub_dev_deleted', self.resp_data)
        return "ack", self.delivery_id

if __name__ == '__main__':
    pass