'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
import syslog

class Loger(object):
    '''
    Object to write messages to syslog
    '''
    
    def __init__(self):
        pass
        '''
        Constructor
        '''
    @staticmethod
    def write(_message):
        message = "[BlackHole] %s" % _message
        syslog.syslog(syslog.LOG_INFO|syslog.LOG_USER,message)

    @staticmethod
    def writeError(_message):
        message = "[BlackHole] %s" % _message
        syslog.syslog(syslog.LOG_ERR|syslog.LOG_USER,message)
    
    @staticmethod    
    def debug(_message):
        message = "[BlackHole - DEBUG] %s" % _message
        syslog.syslog(syslog.LOG_ERR|syslog.LOG_USER,message)        
        
