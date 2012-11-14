#!/usr/bin/env python
from black_hole_gui.chatServer import ChatServer
import asyncore

PORT = 5006
NAME = 'ChatLine'
NUMBER_OF_CONNECTIONS = 2

if __name__ =='__main__':
    s = ChatServer(PORT, NAME,NUMBER_OF_CONNECTIONS)
    try: asyncore.loop()    
    except KeyboardInterrupt: print
