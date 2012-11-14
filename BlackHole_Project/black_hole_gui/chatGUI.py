'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import sys
import traceback
import re
import logging
import locale
import commands
import socket
import threading
import urwid
from urwid import MetaSignals
import language

CHAT_SERVER = "localhost"
CHAT_SERVER_PORT = 5006

class ExtendedListBox(urwid.ListBox):
    """
        Listbow widget with embeded autoscroll
    """
    __metaclass__ = urwid.MetaSignals
    signals = ["set_auto_scroll"]

    def set_auto_scroll(self, switch):
        if type(switch) != bool:
            return
        self._auto_scroll = switch
        urwid.emit_signal(self, "set_auto_scroll", switch)


    auto_scroll = property(lambda s: s._auto_scroll, set_auto_scroll)

    def __init__(self, body):
        urwid.ListBox.__init__(self, body)
        self.auto_scroll = True

    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, "modified", self._invalidate)
        self.body = body
        self._invalidate()
        urwid.connect_signal(body, "modified", self._invalidate)

    def keypress(self, size, key):
        urwid.ListBox.keypress(self, size, key)

        if key in ("page up", "page down"):
            logging.debug("focus = %d, len = %d" % (self.get_focus()[1], len(self.body)))
            if self.get_focus()[1] == len(self.body)-1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False
            logging.debug("auto_scroll = %s" % (self.auto_scroll))

    def scroll_to_bottom(self):
        logging.debug("current_focus = %s, len(self.body) = %d" % (self.get_focus()[1], len(self.body)))

        if self.auto_scroll:
            # at bottom -> scroll down
            self.set_focus(len(self.body))



"""
 -------context-------
| --inner context---- |
|| HEADER            ||
||                   ||
|| BODY              ||
||                   ||
|| DIVIDER           ||
| ------------------- |
| FOOTER              |
 ---------------------

inner context = context.body
context.body.body = BODY
context.body.header = HEADER
context.body.footer = DIVIDER
context.footer = FOOTER

HEADER = Notice line (urwid.Text)
BODY = Extended ListBox
DIVIDER = Divider with information (urwid.Text)
FOOTER = Input line (Ext. Edit)
"""


class chatGUI(object):

    __metaclass__ = MetaSignals
    signals = ["quit","keypress"]

    _palette = [
            ('divider','light green','dark gray', 'standout'),
            ('text','dark gray', 'default'),
            ('bold_text', 'dark gray', 'default', 'bold'),
            ("body", "text"),
            ("footer", "text"),
            ("header", "text"),
        ]

    for type, bg in (
            ("div_fg_", "dark cyan"),
            ("", "default")):
        for name, color in (
                ("red","dark red"),
                ("blue", "dark blue"),
                ("green", "dark green"),
                ("yellow", "yellow"),
                ("magenta", "dark magenta"),
                ("gray", "light gray"),
                ("white", "white"),
                ("black", "black")):
            _palette.append( (type + name, color, bg) )


    def __init__(self, user):
        self.shall_quit = False
        self.user = user
        self.client = None
        #Conecto al server
        urwid.connect_signal(self,'quit',quit)
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((CHAT_SERVER, CHAT_SERVER_PORT))
            self.client = ChatClient(self,client_socket)
            self.client.start()
        except Exception as e:
            raise FailedServerConnection()

    def main(self):
        """ 
            Entry point to start UI 
        """
        self.ui = urwid.raw_display.Screen()
        self.ui.tty_signal_keys('undefined', 'undefined', 'undefined', 'undefined','undefined')
        self.ui.register_palette(self._palette)
        self.build_interface()
        try:
            self.client.sendMessage(_(u"%s login\n") % self.user.userName)
            self.ui.run_wrapper(self.run)
        except Exception as e:
            self.quit()
            raise e
        
    def run(self):
        """ 
            Setup input handler, invalidate handler to
            automatically redraw the interface if needed.

            Start mainloop.
        """

        # I don't know what the callbacks are for yet,
        # it's a code taken from the nigiri project
        def input_cb(key):
            if key == 'esc':
                self.quit()
            if self.shall_quit:
                raise urwid.ExitMainLoop
            self.keypress(self.size, key)

        self.size = self.ui.get_cols_rows()
        self.main_loop = urwid.MainLoop(
                                        self.context,
                                        screen=self.ui,
                                        handle_mouse=False,
                                        unhandled_input=input_cb,
                                        )

        def call_redraw(*x):
            self.draw_interface()
            invalidate.locked = False
            return True
        
        inv = urwid.canvas.CanvasCache.invalidate
        def invalidate (cls, *a, **k):
            inv(*a, **k)
            if not invalidate.locked:
                invalidate.locked = True
                self.main_loop.set_alarm_in(0, call_redraw)
        invalidate.locked = False
        urwid.canvas.CanvasCache.invalidate = classmethod(invalidate)
        try:
            self.main_loop.run()
        except KeyboardInterrupt as e:
            raise e
            
    def quit(self):
        """ 
        Stops the ui, exits the application (if exit=True)
        """
        if self.client:
            self.client.close()
            self.client.join()      
        #urwid.emit_signal(self, "quit")
        self.shall_quit = True
        raise urwid.ExitMainLoop
        
    def build_interface(self):
        """ 
        Call the widget methods to build the UI 
        """
        self.main_loop = None
        self.header = urwid.Text(_("BlackHole Chat:"))
        self.footer = urwid.Edit(u"> ")
        self.divider = urwid.Text("Initializing.")
        self.generic_output_walker = urwid.SimpleListWalker([])
        self.body = ExtendedListBox(self.generic_output_walker)
        self.header = urwid.AttrWrap(self.header, "divider")
        self.footer = urwid.AttrWrap(self.footer, "footer")
        self.divider = urwid.AttrWrap(self.divider, "divider")
        self.body = urwid.AttrWrap(self.body, "body")
        self.footer.set_wrap_mode("space")
        main_frame = urwid.Frame(self.body, 
                                header=self.header,
                                footer=self.divider)        
        self.context = urwid.Frame(main_frame, footer=self.footer)
        self.divider.set_text(("divider",(_("Send Message:  Press [ESC] to quit."))))
        self.context.set_focus("footer")

    def draw_interface(self):
        if self.main_loop: self.main_loop.draw_screen()

    def keypress(self, size, key):
        """ 
            Handle user inputs
        """

        urwid.emit_signal(self, "keypress", size, key)

        # scroll the top panel

        if key in ("page up","page down","up","down"):
            self.body.keypress (size, key)
    
        # resize the main windows
        elif key == "window resize":
            self.size = self.ui.get_cols_rows()
#    
#        elif key in ('ctrl q'):
#            self.quit()
#            self.context.keypress (size, key)
               
        elif key == "enter":
            # Parse data or (if parse failed)
            # send it to the current world
            text = self.footer.get_edit_text()
            self.footer.set_edit_text(u" "*len(text))
            self.footer.set_edit_text(u"")
            if text.strip():
                self.print_sent_message(text)
                #self.print_received_message('Answer')
        else:
            self.context.keypress(size, key)
 
    def print_sent_message(self, text):
        """
            Print a received message
        """
        try:
            message = u"%s: %s\n" % (self.user.userName,text)
            self.client.sendMessage(message)
        except Exception as e:
            raise e
        #self.print_text('[%s] %s:' % (self.get_time(),self.user.getFullName()))
        #self.print_text(text)       
 
    def print_received_message(self, text):
        """
            Print a sent message
        """
        header = urwid.Text('[%s] %s' % (self.get_time(),text))
        header.set_align_mode('left')
        self.print_text(header)
      
    def print_text(self, text):
        """
            Print the given text in the _current_ window
            and scroll to the bottom. 
            You can pass a Text object or a string
        """
        walker = self.generic_output_walker
        if not isinstance(text, urwid.Text):
            text = urwid.Text(text)
        walker.append(text)
        self.draw_interface()
        self.body.scroll_to_bottom()


    def get_time(self):
        """
            Return formated current datetime
        """
        return datetime.now().strftime('%H:%M:%S')
        
#Exceptions
class AlreadyLogged(Exception):
    def __init__(self):
        self.message = _("You are already connected on other session.") 
         
class FailedServerConnection(Exception):
    def __init__(self):
        self.message = _("Cant connect to Chat server.")      
#Client
class ChatClient(threading.Thread):
    def __init__(self,chatGui,connection):
        threading.Thread.__init__(self)
        self.connection = connection    
        self.chatGui = chatGui
        self.stopIt = False

    def sendMessage(self,message):
        try:
            self.connection.send(message.encode("utf-8"))
        except Exception as e:
            pass
        
    def recieveMessage(self):
        message = self.connection.recv(2048)
        return message.decode("utf-8")
    
    def close(self):
        self.stopIt = True
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
 
    def run(self):
        while not self.stopIt:
            message = self.recieveMessage()
            self.chatGui.print_received_message(message)
            
