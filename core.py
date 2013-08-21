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
    host = 'localhost'
    port = 2000
    port_xmpp = 2012

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

        #self.listen()
        self.listen_xmpp()

    def listen(self):
        """listen for events"""
        print('listen', self.host, self.port)
        while True:
            response, addr = self.socket.recvfrom(1024)
            print('receive', response, addr)
            self.call(addr, 'asd', wait=False)

    def listen_xmpp(self):
        """listen for jabber connections"""
        connection_data = b'''<?xml version='1.0'?>
            <stream:stream xmlns:stream='http://etherx.jabber.org/streams'id='1'
            xmlns='jabber:client' from='localhost'>'''

        auth1_data = b'''<iq type='result' from='localhost' id='auth_1'>
            <query xmlns='jabber:iq:auth'>
                <username/>
                <password/>
                <resource/>
            </query>
        </iq>'''

        auth2_data = b'''<iq type='result' from='localhost' id='auth_2'/>'''

        roster_data = b'''<iq id='aab2a' type='result' from='localhost'>
            <query xmlns='jabber:iq:roster'>
                <item jid='sabine@yak' name='sabine' subscription='both'>
                    <group>Family</group>
                </item>
            </query>
        </iq>'''

        list_data = b'''<iq id='aab3a' type='result'/><iq id='aab5a' type='result'/>'''

        print('listen xmpp', self.host, self.port_xmpp)
        self.socket_xmpp = socket.socket()
        self.socket_xmpp.bind((self.host, self.port_xmpp))
        self.socket_xmpp.listen(5)
        connect, addr = self.socket_xmpp.accept()
        print('connect xmpp', connect, addr)

        # connection
        data = connect.recv(1024)
        print('receive', data)
        connect.send(connection_data)
        print('send   ', connection_data)

        data = connect.recv(1024)
        print('receive', data)
        connect.send(auth1_data)
        print('send   ', auth1_data)

        data = connect.recv(1024)
        print('receive', data)
        connect.send(auth2_data)
        print('send   ', auth2_data)

        data = connect.recv(1024)
        print('receive', data)
        connect.send(roster_data)
        print('send   ', roster_data)

        data = connect.recv(1024)
        print('receive', data)
        connect.send(list_data)
        print('send   ', list_data)

        data = connect.recv(1024)
        print('receive', data)
        data = connect.recv(1024)
        print('receive', data)


class Node(NodeBase):
    """known node"""


if __name__ == '__main__':
    opts = {}
    if len(sys.argv) == 3:
        opts['port'] = int(sys.argv[1])
        opts['db_name'] = sys.argv[2]
    Watashi(**opts)
