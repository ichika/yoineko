#!/usr/bin/env python3

import sys
import socket
import json

import db


class NodeBase:
    """base class of node"""
    def call(self, addr, msg, wait=True):
        """do request to other node and return result"""
        request = bytes(json.dumps(msg), 'utf-8')
        print('request', request)
        self.socket.sendto(request, addr)

        if wait:
            response, addr = self.socket.recvfrom(1024)
            print('response', response)
            return json.loads(response.decode())


class Watashi(NodeBase):
    """my node"""
    host = '127.0.0.1'
    port = 2000

    def __init__(self, port=None, db_name='data'):
        """run my node"""
        db.init(db_name)

        if port:
            self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        for node in db.Node.select():
            print('exist', node, node.addr, node.port)
            self.call(node.addr, 'hello')

        self.listen()

    def listen(self):
        """listen for events"""
        print('listen', self.host, self.port)
        while True:
            response, addr = self.socket.recvfrom(1024)
            print('receive', response, addr)
            self.call(addr, 'asd', wait=False)


class Node(NodeBase):
    """known node"""


if __name__ == '__main__':
    opts = {}
    if len(sys.argv) == 3:
        opts['port'] = int(sys.argv[1])
        opts['db_name'] = sys.argv[2]
    Watashi(**opts)
