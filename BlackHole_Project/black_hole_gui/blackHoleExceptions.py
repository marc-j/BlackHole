'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
from loger import Loger
import language

class FileMissing(Exception):
    def __init__(self, fileName):
        self.fileName = fileName
        self.message = _("File %s is Missing") % self.fileName
        Loger.writeError(self.message)

class ErroLoadingData(Exception):
    def __init__(self, _message):
        self.message = _("Error Loading Settings: %s") % _message   
        Loger.writeError(self.message)
    
class UnknownUser(Exception):
    def __init__(self, userName):
        self.message = _("Unknown User [%s]") % userName
        Loger.writeError(self.message)

class UserDisabled(Exception):
    def __init__(self, user):
        self.message = _("The user %s is not enabled.") % user.getFullName()
        Loger.writeError(self.message)
        
class MysqlException(Exception):
    def __init__(self, _message=""):
        self.message = _("DataBase Error: %s ") % _message   
        Loger.writeError(self.message)
        
class UserDisabledTime(Exception):
    def __init__(self, user):
        messageString = _("The user %(username)s is only enabled from %(from)s to %(to)s")
        self.message = messageString % {'username':user.getFullName(),
                                            'from':user.timeFrom,
                                            'to':user.timeTo}
        Loger.writeError(self.message)         
        
