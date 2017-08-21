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
    
    def __init__(self, product_key, auth_id, auth_secret, events = DEFAULT_EVENTS, subkey = DEFAULT_SUBKEY):
        self.__product_key = product_key
        self.__auth_id = auth_id
        self.__auth_secret = auth_secret
        self.__events = events
        self.__subkey = subkey
        self.__online = False
        self.__recv_thread = None
        self.__ping_thread = None
        self.__create_handler()
        # callback function
        self._callback = None

    def __create_handler(self):
        self.__handler = {
            'login_success': self.__handle_login_success,
            'login_fault': self.__handle_login_fault,
            'pong': self.__pong,
            'ack': self.__ack
        }

    def connect(self, snoti_host = DEFAULT_HOST, snoti_port = DEFAULT_PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket create success")
        ssl_sock = ssl.wrap_socket(s)
        ssl_sock.connect((snoti_host, snoti_port))
        print("socket connect success")
        self.ssl_sock = ssl_sock
        self.__login()
        if self.__recv_thread == None:
            self.__recv_thread = threading.Thread(target=self.__recv_data, args=())
            self.__recv_thread.setDaemon(True)
            self.__recv_thread.start()

    def disconnect(self):
        self.__online = False
        self.ssl_sock.close()

    def control_kv(self, did, mac, attrs):
        if self.__online:
            req = ControlReq()
            req.add_control_kv('write_attrs', did, mac, self.__product_key, attrs)
            req.build_json()
            self.ssl_sock.sendall(str.encode(repr(req)))

    def __login(self):
        req = LoginReq()
        req.add_login_data(self.__product_key, self.__auth_id, self.__auth_secret, self.__subkey, self.__events)
        req.build_json()
        self.ssl_sock.sendall(str.encode(repr(req)))
    
    def __ping(self):
        req = Request('ping')
        req.build_json()
        while self.__online:
            self.ssl_sock.sendall(str.encode(repr(req)))
            sleep(self.HEAERBEAT_TIME)

    def __ack(self, delivery_id):
        print('ack: %s' % (delivery_id))
        req = AckReq(delivery_id)
        req.build_json()
        print(req)
        if self.__online:
            self.ssl_sock.sendall(str.encode(repr(req)))

    def __recv_data(self):
        while True:
            rev_data = self.ssl_sock.recv(1024)
            if rev_data:
                self.__handle_recv(rev_data)
            else:
                break
        self.ssl_sock.close()
    
    def __handle_recv(self, rev_data):
        resp = response.Response(rev_data)
        handle_result, result_data = resp.handle(self)
        if handle_result in self.__handler.keys():
            self.__handler[handle_result](result_data)
    
    def __handle_login_success(self, *args):
        print('login success')
        self.__online = True
        if self.__ping_thread == None:
            self.__ping_thread = threading.Thread(target=self.__ping, args=())
            self.__ping_thread.setDaemon(True)
            self.__ping_thread.start()
    
    def __handle_login_fault(self, *args):
        print('login fault')
        sleep(3)
        self.login()
    
    def __pong(self, *args):
        print('pong')
        pass

if __name__ == '__main__':
    client = Client("c74fd6e832eb42de80540d7d738fe025", "9UDAyB8pQY6w2HSewJmwvw", "r5A9PhsYQIGhJ03SSOsIqQ", subkey="sandbox_000")
    import callback
    client.callback = callback
    client.connect()
    sleep(20)
    client.control_kv("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", {"number":5})
    sleep(60)
    client.disconnect()

