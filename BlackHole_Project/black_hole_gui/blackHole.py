'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
import os
import sys
import getpass
import socket
from loger import Loger
from ConfigParser import ConfigParser
from django.core.management import setup_environ
import random   
from django.core import exceptions
from datetime import datetime
import paramiko
from _mysql_exceptions import OperationalError 
from blackHoleExceptions import UserDisabledTime, UnknownUser, UserDisabled, ErroLoadingData, MysqlException, FileMissing
import cursesGui
import black_hole.settings
setup_environ(black_hole.settings)
from black_hole_db.models import User, PrivateKey, SessionLog
from tokenValidationWindow import TokenValidationWindow
from loger import Loger
import language

class Settings(object):
    def __init__(self, configParserObject):
        section = 'settings'
        self.debug = configParserObject.getboolean(section, 'debug')
        self.application_path = configParserObject.get(section, 'application_path')  
        self.log_path = configParserObject.get(section, 'log_path') 
        self.chat_enabled = configParserObject.getboolean(section, 'chat_enabled')
        self.token_validation_enabled = configParserObject.getboolean(section, 'token_validation_enabled')
        if not os.path.isdir(self.application_path):
            raise ErroLoadingData('Path %s does not exists' % self.application_path)
        if not os.path.isdir(self.log_path):
            raise ErroLoadingData('Path %s does not exists' % self.log_path)

class Data(object):
    def __init__(self):
        try:
            self.user = User.objects.get(userName=getpass.getuser())
        except exceptions.ObjectDoesNotExist as e:
            raise UnknownUser(getpass.getuser())
        except Exception as e:
            raise e
        try:
            self.sourceIP = str(os.environ.get('SSH_CLIENT')).split()[0]
        except:
            self.sourceIP = '0.0.0.0'
        try:
            self.clientPort = str(os.environ.get('SSH_CLIENT')).split()[1]
        except:
            self.clientPort = 0
        self.sessionID = random.randrange(100000, 999999, 1)

class BlackHole(object):
    """The main class of the application"""
    def __init__(self, SETTINGS_FILE):
        """
        Creates an instance of BlackHole
        Arguments:
        SETTINGS_FILE: Path of the settings File
        """
        self.settings = None
        self.data = None
        self.information = None
        try:
            self._loadData(SETTINGS_FILE)
            Loger.write(self)  
            if self.data.user.enable:
                if self.data.user.timeEnabled:
                    now = datetime.now().time().replace(second=0)
                    if not (self.data.user.timeFrom < now < self.data.user.timeTo):
                        raise UserDisabledTime(self.data.user)
                self.data.user.lastLogin = datetime.now()
                self.data.user.save()
            else:
                raise UserDisabled(self.data.user)       
            self.blackHoleBrowser = cursesGui.BlackHoleBrowser(self)
        except OperationalError as e:
            raise MysqlException(e)
        except Exception as e:
            raise e
    
    def main(self):
        """
        Main method, it runs the app.
        """
        #Check if the app is set to generate and send tokens
        if self.settings.token_validation_enabled:
            #Check if the user needs to be verified by token
            if self.data.user.generateToken:
                w = TokenValidationWindow(self.data,self.settings)
                w.main()
        #Start the browser
        self.blackHoleBrowser.main()
    
    def _loadData(self, SETTINGS_FILE):
        """
        Load settings from settings file.
        Arguments:
        SETTINGS_FILE: Path of the settings File
        """
        config = ConfigParser()
        try:
            config.read(SETTINGS_FILE)
            self.settings = Settings(config)  
            self.data = Data()
        except IOError:
            raise FileMissing(SETTINGS_FILE)
        except Exception as e:
            raise e
    
    def __str__(self):
        return("[auth] user=%s sessionID=%s from=%s:%s" % (self.data.user.userName, self.data.sessionID, self.data.sourceIP, self.data.clientPort))
    
    def getPrivateKey(self, user, environment):
        try:
            pk = PrivateKey.objects.get(user=user, environment=environment)
            try:
                if pk.type == 'DSA':
                    key = paramiko.DSSKey.from_private_key(pk)
                else:
                    key = paramiko.RSAKey.from_private_key(pk)   
            except Exception as e:
                Loger.writeError("%s [%s]" % (user, e.message))
                return False             
            return key
        except exceptions.ObjectDoesNotExist as e:
            return False
        
    def writeSessionLog(self, host, userIdentity, loginDate, logoutDate, sessionDuration, usage, keyCount, logFile):
        try:
            blackholeServer = socket.gethostname()
            sessionLog = SessionLog(user=self.data.user,
                                       host=host,
                                       userIdentity=userIdentity,
                                       sourceIP=self.data.sourceIP,
                                       loginDate=loginDate,
                                       logoutDate=logoutDate,
                                       sessionID=self.data.sessionID,
                                       sessionDuration=sessionDuration,
                                       usage = usage,
                                       keyCount = keyCount,
                                       blackholeServer = blackholeServer,
                                       logFile = logFile)
            sessionLog.save()
        except Exception as e:
            Loger.writeError("!!%s [%s]" % (self.data.user.userName,e))
        
