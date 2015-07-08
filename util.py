#encoding=utf-8
#+-------------------------------------------------------+
# wspy.util
# Copyright (c) 2015 OshynSong<dualyangsong@gmail.com>
#
# Construct socket connection pool
#+-------------------------------------------------------+
'''
wspy.util
This module contains the connection of socekt and the pool
maintaince for the web client request.
'''
import sys
import os
import socket
import re
import types
import uuid
from hashlib import sha1, md5

from error import *

class SocketPool(list):
    '''All of the connected socket array'''
    def __init__(self, li=[]):
        super(SocketPool, self).__init__(li)
        
class Client(object):
    '''The client connection, identified by uuid'''
    def __init__(self, sock, timeout=30, handshake=False):
        if sock == None:
            raise NetworkError('Client socket is None!')
        if not isinstance(timeout, types.IntType) or timeout <= 0:
            raise WSTypeError('Timeout value or type is invalid!')
        uid = uuid.uuid1().get_hex()
        self.Uid      = sha1(uid).hexdigest()
        self.Sock     = sock
        self.Timeout  = timeout
        self.Handshake= handshake
    def __str__(self):
        return 'Client: %s; Timeout: %d s; Handshake %s' \
                % (self.Uid, self.Timeout, str(self.Handshake))
    def decTimeSec(self):
        self.Timeout  = self.Timeout - 1
        
class ClientPool(dict):
    '''Client connection pool maintance by the server'''
    def __setattr__(self, uuid, cli):
        self[uuid] = cli
        
    def __getattr__(self, uuid):
        if self.has_key(uuid) and self[uuid] != None:
            return self[uuid]
        else: return None

class WSSocket(object):
    '''The client connection socket class
    Each client connection has a uid for identification
    and a timeout for remove from the pool.
    '''
    def __init__(self, addr, port):
        self.Sockets = SocketPool()
        self.Clients = ClientPool()
        if isinstance(addr, types.StringType):
            if addr == 'localhost': pass
            else:
                a = re.match(r'([0-9]{1,3}\.){3}[0-9]{1,3}', addr)
                if a.group() == addr: pass
                else: raise WSError('Not valid address')
        else: raise WSTypeError('Address type error.')
        if isinstance(port, types.IntType):
            if port > 1024 and port < 65536: pass
            else: raise WSError('Not valid port.')
        else: raise WSTypeError('Port type error.')
        self.Host    = self.__createHost((str(addr), int(port)))
        self.Sockets.append(self.Host)
    
    def __createHost(self, ap):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(ap)
        sock.listen(100)
        return sock

if __name__ == '__main__':
    #li = SocketPool()
    #li.append('socket')
    #print li
    #c = Client('clientsock')
    #cp= ClientPool()
    #cp[c.Uid] = c
    #print cp[c.Uid].Sock
    #ws = WSSocket('127.0.0.1', 5005)
    #print ws.Clients
    #print ws.Host
    #print ws.Sockets
    #ws.Host.close()
    #print sha1('123').hexdigest()
    #print sha1('123').digest()
    pass