#! python3
# -*- coding: utf-8 -*-
import socket
import ssl
import threading
from time import sleep
if __name__ == '__main__':
    import response
    from request import Request, LoginReq, AckReq, ControlReq
    from settings import LOGGING_CONFIG
    import callback
else:
    from . import response
    from .request import Request, LoginReq, AckReq, ControlReq
    from .settings import LOGGING_CONFIG
    from . import callback

# logging
import logging
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger('client')

class Client:
    DEFAULT_EVENTS = ['device.attrs_fault',
                      'device.attr_alert',
                      'device.online',
                      'device.offline',
                      'device.status.raw',
                      'device.status.kv',
                      'datapoints.changed',
                      'center_control.sub_device_added',
                      'center_control.sub_device_deleted']
    DEFAULT_SUBKEY = 'default'
    HEAERBEAT_TIME = 120
    MAX_MISS_PONG = 2    # 客户端在第MAX_MISS_PONG+1次发送心跳前，都没有收到过服务器消息，则判定为连接断开
    DEFAULT_HOST = 'snoti.gizwits.com'
    DEFAULT_PORT = 2017
    
    def __init__(self, product_key, auth_id, auth_secret, events = DEFAULT_EVENTS, subkey = DEFAULT_SUBKEY, callback = callback):
        self._product_key = product_key
        self._auth_id = auth_id
        self._auth_secret = auth_secret
        self._events = events
        self._subkey = subkey
        self._online = False
        self._recv_thread = None
        self._ping_thread = None
        self._create_handler()
        # 回调模块
        self._callback = callback

    # 通过返回字符串，对应后续执行的函数
    def _create_handler(self):
        self._handler = {
            'login_success': self._handle_login_success,
            'login_fault': self._handle_login_fault,
            'not_login': self._handle_not_login,
            'has_login': self._handle_has_login,
            'pong': self._pong,
            'ack': self._ack
        }

    def connect(self, snoti_host = DEFAULT_HOST, snoti_port = DEFAULT_PORT):
        self._snoti_host = snoti_host
        self._snoti_port = snoti_port
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info("socket create success")
            ssl_sock = ssl.wrap_socket(s)
            ssl_sock.connect((snoti_host, snoti_port))
            logger.info("socket connect success")
            self.ssl_sock = ssl_sock
            self._login()
            if self._recv_thread == None:
                self._recv_thread = threading.Thread(target=self._recv_data, args=())
                self._recv_thread.setDaemon(True)
                self._recv_thread.start()
        except socket.error as e:
            logger.info("Socket连接失败: %s\n10秒后重试..." % (e))
            try:
                s.close()
            except Exception:
                pass
            finally:
                sleep(10)
                self._reconnect()

    def _reconnect(self):
        self._online = False
        try:
            self.ssl_sock.close()
        except Exception:
            pass
        finally:
            self.connect(self._snoti_host, self._snoti_port)

    def disconnect(self):
        self._online = False
        self.ssl_sock.close()

    # data的数据类型为Hex字符串
    def control_raw(self, did, mac, data, msg_id = None):
        raw = [item for item in bytes().fromhex(data)]
        req = ControlReq(msg_id)
        req.add_control_raw('write', did, mac, self._product_key, raw)
        payload = req.build_json()
        logger.info(payload)
        self.ssl_sock.sendall(str.encode(payload))

    def control_kv(self, did, mac, attrs, msg_id = None):
        req = ControlReq(msg_id)
        req.add_control_kv('write_attrs', did, mac, self._product_key, attrs)
        payload = req.build_json()
        logger.info(payload)
        self.ssl_sock.sendall(str.encode(payload))

    def _login(self):
        req = LoginReq()
        req.add_login_data(self._product_key, self._auth_id, self._auth_secret, self._subkey, self._events)
        payload = req.build_json()
        self._send_data(payload)
    
    def _ping(self):
        req = Request('ping')
        payload = req.build_json()
        while True:
            if self._online:
                self._send_data(payload)
                self._wait_pong_count += 1
                if self._wait_pong_count > self.MAX_MISS_PONG:
                    logger.info("Socket异常断开，正在重新尝试连接...")
                    self._reconnect()
            sleep(self.HEAERBEAT_TIME)
        self._ping_thread = None

    def _ack(self, delivery_id):
        logger.info('ack: %s' % (delivery_id))
        req = AckReq(delivery_id)
        payload = req.build_json()
        self._send_data(payload)

    def _send_data(self, payload):
        try:
            self.ssl_sock.sendall(str.encode(payload))
        except socket.error:
            logger.info("Socket异常断开，正在重新尝试连接...")
            self._reconnect()

    def _recv_data(self):
        rev_data = ''
        while True:
            try:
                rev_data += bytes.decode(self.ssl_sock.recv(1024))
                if rev_data:
                    payloads = rev_data.split('\n')
                    rev_data = payloads.pop(-1)
                    for item in payloads: self._handle_recv(item)
            except Exception as e:
                logger.warn(e)
                break
        self._recv_thread = None

    def _handle_recv(self, rev_data):
        self._wait_pong_count = 0  #收到服务器数据，说明与服务器的连接正常，即清0
        try:
            resp = response.Response(rev_data)
            handle_result, result_data = resp.handle(self._callback)
            if handle_result in self._handler.keys():
                self._handler[handle_result](result_data)
        except Exception as e:
            if rev_data == 'No Heartbeat!':
                logger.warn('客户端与服务器断开连接，尝试重连...')
                self._reconnect()
            else:
                logger.error('客户端解析数据异常: %s' % (e))
    
    def _handle_login_success(self, *args):
        logger.info('login success')
        self._online = True
        self._wait_pong_count = 0
        if self._ping_thread == None:
            self._ping_thread = threading.Thread(target=self._ping, args=())
            self._ping_thread.setDaemon(True)
            self._ping_thread.start()
    
    def _handle_login_fault(self, errmsg):
        logger.info('登录失败，请根据错误日志判断是否为客户端参数错误: %s，\n5秒钟后会重新尝试...' % (errmsg))
        sleep(5)
        self._login()
    
    def _handle_not_login(self, errmsg):
        logger.info('客户端异常：%s，请重新发送指令...' % (errmsg))
        self._online = False
        self._login()
    
    def _handle_has_login(self, errmsg):
        self._online = True
    
    def _pong(self, *args):
        logger.info('pong')
        pass

if __name__ == '__main__':
    import callback
    client = Client("c74fd6e832eb42de80540d7d738fe025", "9UDAyB8pQY6w2HSewJmwvw", "r5A9PhsYQIGhJ03SSOsIqQ", subkey="sandbox_000")
    client.connect()
    sleep(20)
    client.control_kv("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", {"binary":[0,1,255,0,0]})
    # sleep(60)
    # client.control_raw("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", "02")
    # sleep(60)
    sleep(500)


