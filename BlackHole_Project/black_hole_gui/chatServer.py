#!/usr/bin/python
'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-

from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore
import language

class ChatSession(async_chat):
    def __init__(self,server,sock,user="Unknown"):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\n")
        self.data = []
        self.user = user

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = "".join(self.data)
        self.data = []
        self.server.broadcast(line)

    def handle_close(self):
        async_chat.handle_close(self)
        self.server.disconnect(self)

class ChatServer(dispatcher):
    def __init__(self, port, name, numberOfConnections):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("",port))
        self.listen(numberOfConnections)
        self.name = name
        self.sessions = []
  
    def disconnect(self, session):
        print("%s %s" % (_("Disconnect"),session))
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line.rstrip('\n'))

    def handle_accept(self):
        conn, addr = self.accept()
        print(conn,addr)
        #Verificar que no esta conctado
        self.sessions.append(ChatSession(self, conn))

