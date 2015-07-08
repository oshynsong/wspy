#encoding=utf-8
#+-------------------------------------------------------+
# wspy.server
# Copyright (c) 2015 OshynSong<dualyangsong@gmail.com>
#
# This the detail implements of websocket protocol.
#+-------------------------------------------------------+
'''
wspy.server
This module contains the collection of websocket protocol
implements and tackle.
'''
import os
import sys
import socket, select
import time
import struct
import re
import base64
from hashlib import sha1, md5

from error import *
from util import *

IOTYPE = ['select', 'pool', 'async']

class WS(WSSocket):
    ''''''
    def __init__(self, addr, port, ioType = 'select'):
        if ioType not in IOTYPE:
            raise WSTypeError('IO type not valid.')
        self.IO = ioType
        super(WS, self).__init__(addr, port)
        self.say('Server started : ' + time.strftime('%Y-%m-%d %H:%M:%S'))
        self.say('Host socket    : ' + str(self.Host))
        self.say('Listening on   : ' + addr + ':' + str(port))
    
    def run(self):
        while True:
            rs, ws, es = select.select(self.Sockets, [], [])
            for r in rs:
                if r == self.Host:
                    cliSock, addr = self.Host.accept()
                    if not cliSock:
                        self.log('Socket accept failed.')
                        continue
                    else:
                        self.connect(cliSock)
                else:
                    try:
                        data = r.recv(2048)
                        if len(data) == 0:
                            self.disConnect(r)
                        else:
                            cli = None
                            for k,v in self.Clients.items():
                                if v.Sock == r: cli = v
                            if cli != None:
                                if not cli.Handshake:
                                    self.doHandShake(cli, data)
                                else:
                                    self.process(cli, data)
                    except socket.error:
                        self.disConnect(r)
                        continue
        
    def pack(self, msg, first = 0x80, opcode = 0x01):
        firstByte  = first | opcode
        encodeData = None
        cnt        = len(msg)
        if cnt >= 0 and cnt <= 125:
            encodeData = struct.pack('BB', firstByte, cnt) + msg
        elif cnt >= 126 and cnt <= 0xFFFF:
            #low  = cnt & 0x00FF
            #high = (cnt & 0xFF00) >> 8
            encodeData = struct.pack('>BBH', firstByte, 0x7E, cnt) + msg
        else:
            low  = cnt & 0x0000FFFF
            high = (cnt & 0xFFFF0000) >> 16
            encodeData = struct.pack('>BBLL', firstByte, 0x7F, high, low) + msg
        return encodeData
    
    def unpack(self, cliSock, msg):
        opcode = ord(msg[0:1]) & 0x0F
        mask   = (ord(msg[1:2]) & 0x80) >> 7
        pllen1 = ord(msg[1:2]) & 0x7F
        oriData    = ''
        maskKey    = ''
        decodeData = ''
        
        #Close the connection or mask bit not set
        if opcode == 0x8:
            self.disConnect(cliSock)
            return None
        if mask != 1:
            raise UnmaskError('Mask bit is not set from client.')
        
        #Get mask key and original data
        if pllen1 >= 0 and pllen1 <= 125:
            maskKey = msg[2:6]
            oriData = msg[6:]
        elif pllen1 == 126:
            maskKey = msg[4:8]
            oriData = msg[8:]
        else:
            maskKey = msg[10:14]
            oriData = msg[14:]
        
        #Decode the masked original data
        l = len(oriData) ;print l
        for i in range(l):
            decodeData += chr(ord(oriData[i]) ^ ord(maskKey[i % 4]))
        return decodeData
    
    def send(self, cli, msg, isLast = True, opcode = 1):
        self.say('> Send to client ' + cli.Uid + ':\n' + msg)
        if isLast: first = 0x80
        else: first = 0x00
        msg = self.pack(msg, first, opcode)
        cli.Sock.send(msg)
    
    def process(self, cli, msg):
        msg = self.unpack(cli.Sock, msg)
        if msg != None:
            self.say('< Get from client ' + cli.Uid + ':\n' + msg)
            self.send(cli, msg, False)
            self.send(cli, msg, False, 0)
            self.send(cli, msg, True, 0)
    
    def getHeaders(self, data):
        resource = re.match(r'GET (.*?) HTTP', data)
        host     = re.search(r'Host: (.*?)\r\n', data)
        origin   = re.search(r'Origin: (.*?)\r\n', data)
        key      = re.search(r'Sec-WebSocket-Key: (.*?)\r\n', data)
        resource = resource.group(1) if resource != None else None
        host     = host.group(1) if host != None else None
        origin   = origin.group(1) if origin != None else None
        key      = key.group(1) if key != None else None
        return resource, host, origin, key
    
    def doHandShake(self, cli, data):
        self.log(data)
        resource, host, origin, key = self.getHeaders(data)
        self.log('Requesting handshake: %s ...' % host)
        print host, origin; print key
        #websocket version 13
        sha1Encrypt = sha1(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest()
        acceptKey   = base64.b64encode(sha1Encrypt)
        self.log('Handshaking...')
        upgrade = 'HTTP/1.1 101 Switching Protocol\r\n' + \
                  'Upgrade: websocket\r\n' + \
                  'Connection: Upgrade\r\n' + \
                  'Sec-WebSocket-Accept: ' + acceptKey + \
                  '\r\n\r\n'
        self.log(upgrade)
        cli.Sock.send(upgrade)
        cli.Handshake = True
        self.log('Handshake Done.')
        return True
    
    def connect(self, cliSock, timeout=30, handshake=False):
        cli = Client(cliSock, timeout, handshake)
        self.Clients[cli.Uid] = cli
        self.Sockets.append(cliSock)
        self.log(cli.Uid + ' CONNECTED!')
        
    def disConnect(self, cliSock):
        inSockets = -1
        inClients = ''
        for i,s in enumerate(self.Sockets):
            if s == cliSock:
                del self.Sockets[i]
                inSockets = i
                break
        for k,v in self.Clients.items():
            if v.Sock == cliSock:
                del self.Clients[k]
                inClients = k
                break
        if inSockets != -1 and inClients != '':
            cliSock.close()
            self.log('Client socket %s Disconnected' % inClients)
    
    def log(self, msg = ''):
        '''The msg log for server'''
        fmt = '%Y-%m-%d %H:%M:%S'
        print '[%s]\n%s' % (time.strftime(fmt), msg)
    
    def say(self, msg = ''):
        '''The msg write to client'''
        print msg.decode('utf8').encode('gbk')

if __name__ == '__main__':
    ws = WS('127.0.0.1', 5005)
    ws.run()
