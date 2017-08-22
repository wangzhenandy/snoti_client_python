#! python3
# -*- coding: utf-8 -*-
import socket
import ssl
import response
import threading
from time import sleep
from request import Request, LoginReq, AckReq, ControlReq

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
    DEFAULT_HOST = 'snoti.gizwits.com'
    DEFAULT_PORT = 2017
    
    def __init__(self, product_key, auth_id, auth_secret, events = DEFAULT_EVENTS, subkey = DEFAULT_SUBKEY, callback = None):
        self._product_key = product_key
        self._auth_id = auth_id
        self._auth_secret = auth_secret
        self._events = events
        self._subkey = subkey
        self._online = False
        self._recv_thread = None
        self._ping_thread = None
        self._create_handler()
        # callback function
        self._callback = callback

    def _create_handler(self):
        self._handler = {
            'login_success': self._handle_login_success,
            'login_fault': self._handle_login_fault,
            'pong': self._pong,
            'ack': self._ack
        }

    def connect(self, snoti_host = DEFAULT_HOST, snoti_port = DEFAULT_PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket create success")
        ssl_sock = ssl.wrap_socket(s)
        ssl_sock.connect((snoti_host, snoti_port))
        print("socket connect success")
        self.ssl_sock = ssl_sock
        self._login()
        if self._recv_thread == None:
            self._recv_thread = threading.Thread(target=self._recv_data, args=())
            self._recv_thread.setDaemon(True)
            self._recv_thread.start()

    def disconnect(self):
        self._online = False
        self.ssl_sock.close()

    def control_kv(self, did, mac, attrs):
        if self._online:
            req = ControlReq()
            req.add_control_kv('write_attrs', did, mac, self._product_key, attrs)
            payload = req.build_json()
            self.ssl_sock.sendall(str.encode(payload))

    def _login(self):
        req = LoginReq()
        req.add_login_data(self._product_key, self._auth_id, self._auth_secret, self._subkey, self._events)
        payload = req.build_json()
        self.ssl_sock.sendall(str.encode(payload))
    
    def _ping(self):
        req = Request('ping')
        payload = req.build_json()
        while self._online:
            self.ssl_sock.sendall(str.encode(payload))
            sleep(self.HEAERBEAT_TIME)

    def _ack(self, delivery_id):
        print('ack: %s' % (delivery_id))
        req = AckReq(delivery_id)
        payload = req.build_json()
        print(req)
        if self._online:
            self.ssl_sock.sendall(str.encode(payload))

    def _recv_data(self):
        while True:
            rev_data = self.ssl_sock.recv(1024)
            if rev_data:
                self._handle_recv(rev_data)
            else:
                break
        self.ssl_sock.close()
    
    def _handle_recv(self, rev_data):
        resp = response.Response(rev_data)
        handle_result, result_data = resp.handle(self._callback)
        if handle_result in self._handler.keys():
            self._handler[handle_result](result_data)
    
    def _handle_login_success(self, *args):
        print('login success')
        self._online = True
        if self._ping_thread == None:
            self._ping_thread = threading.Thread(target=self._ping, args=())
            self._ping_thread.setDaemon(True)
            self._ping_thread.start()
    
    def _handle_login_fault(self, *args):
        print('login fault')
        sleep(3)
        self._login()
    
    def _pong(self, *args):
        print('pong')
        pass

if __name__ == '__main__':
    import callback
    client = Client("c74fd6e832eb42de80540d7d738fe025", "9UDAyB8pQY6w2HSewJmwvw", "r5A9PhsYQIGhJ03SSOsIqQ", subkey="sandbox_000", callback = callback)
    client.connect()
    sleep(20)
    client.control_kv("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", {"number":5})
    sleep(60)
    client.disconnect()

