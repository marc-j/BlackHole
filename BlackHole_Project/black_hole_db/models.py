# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext as _


class Environment(models.Model):
    name = models.CharField(max_length=15, unique=True, verbose_name=_("Name"))
    description = models.CharField(max_length=50, verbose_name=_("Description"))             
    
    def __unicode__(self):
        return(u"%s" % self.description)

    class Meta(object):
        verbose_name = _("Environment")
        verbose_name_plural = _("Environments")
        ordering = ['name']

class Host(models.Model):
    OS_CHOICES = (
                  ('LINUX', 'Linux'),
                  ('SOLARIS', 'Solaris'),
                  ('OSX', 'Mac OSX'),
                  ('WINDOWS', 'Windows'),
                  )
    
    name = models.CharField(max_length=30, unique=True, verbose_name=_("Name"))
    ip = models.IPAddressField(verbose_name=_("IP Address"))
    port = models.PositiveIntegerField(max_length=5, default=22, verbose_name=_("Port"))
    os = models.CharField(max_length=10, choices=OS_CHOICES, default=0, verbose_name=_("Operative System"))
    description = models.CharField(max_length=50, verbose_name=_("Description"))
    environment = models.ForeignKey(Environment, verbose_name=_("Environment")) 
    
    def __unicode__(self):
        return(u"%s [%s] [%s]" % (self.name, self.ip, self.environment))
    
    class Meta(object):
        verbose_name = _("Host")
        verbose_name_plural = _("Hosts")
        ordering = ['name']

class UserIdentity(models.Model):    
    username = models.CharField(max_length=20, unique=True, verbose_name=_("User"))
   
    def __unicode__(self):
        return(u"%s" % self.username)

    class Meta(object):
        verbose_name = _("User Identity")
        verbose_name_plural = _("User Identities")
        ordering = ['username']
   
class PrivateKey(models.Model):
    TYPE_CHOICES = (
                    ('DSA', 'DSA Key'),
                    ('RSA', 'RSA Key'),
                    )
    user = models.CharField(max_length=20, verbose_name=_("User"))
    environment = models.ForeignKey(Environment, verbose_name=_("Environment"))
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, verbose_name=_("Key Type"))
    privateKey = models.TextField(verbose_name=_("Private Key"))
    publicKey = models.TextField(verbose_name=_("Public Key"))
    
    def __unicode__(self):
        return(u"%s [%s]" % (self.user, self.environment.name))
    
    def readlines(self):
        pk_to_string = str(self.privateKey).replace('\r', '') 
        return(pk_to_string.split('\n'))
    
    class Meta(object):
        unique_together = ('user', 'environment')
        verbose_name = _("Private Key")
        verbose_name_plural = _("Private Keys")
        ordering = ['user', 'environment']
    
class HostConnection(models.Model):
    host = models.ForeignKey(Host, verbose_name=_("Host"))
    userAuthentication = models.ForeignKey(UserIdentity, verbose_name=_("Login As"))
    
    def __unicode__(self):
        return(u"%s as %s" % (self.host, self.userAuthentication))
    
    def getConnectionUser(self, user):
        if self.userAuthentication.username == "self":
            return u"%s" % user.userName
        else:
            return u"%s" % self.userAuthentication.username

    class Meta(object):
        unique_together = ('host', 'userAuthentication')
        verbose_name = _("Session Identity")
        verbose_name_plural = _("Session Identities")
        ordering = ['host', 'userAuthentication']

class Profile(models.Model):
    name = models.CharField(max_length=15, unique=True, verbose_name=_("Name")) 
    hosts = models.ManyToManyField(HostConnection, blank=True, verbose_name=_("Hosts"))   
    
    def getEnvironments(self):
        environmentList = []
        for environment in Environment.objects.all().order_by('name'):
            if len(self.hosts.filter(host__environment=environment)) > 0:
                environmentList.append(environment)
        return environmentList

    def __unicode__(self):
        return(u"%s" % self.name)      

    class Meta(object):
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ['name']
 
class User(models.Model):
    userName = models.CharField(max_length=20, unique=True, verbose_name=_("User"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    lastName = models.CharField(max_length=50, verbose_name=_("LastName"))
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    identifier = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Identifier"))
    profile = models.ForeignKey(Profile, verbose_name=_("Profile"))
    enable = models.BooleanField(default=True, verbose_name=_("Enabled"))
    logEnable = models.BooleanField(default=True, verbose_name=_("Log Session"))
    timeEnabled = models.BooleanField(default=False, verbose_name=_("Enabled in Time Range"))
    timeFrom = models.TimeField(default=(lambda:datetime.now().time().replace(second=0)), verbose_name=_("Since"))
    timeTo = models.TimeField(default=(lambda:datetime.now().time().replace(second=0)), verbose_name=_("To"))
    allowedByEnvironments = models.ManyToManyField(Environment, blank=True, verbose_name=_("Enabled Environments"))
    lastLogin = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Login"))
    generateToken = models.BooleanField(default=False, verbose_name=_("Generate Token"))
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Celular Phone"))

    def getFullName(self):
        return(u"%s, %s [%s]" % (self.lastName, self.name, self.userName))
    
    def __unicode__(self):
        return(u"%s, %s [%s]" % (self.lastName, self.name, self.userName))

    class Meta(object):
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['userName']
        
class SessionLog(models.Model):
    sessionID = models.IntegerField(verbose_name=_("Session ID"))
    user = models.ForeignKey('User',verbose_name=_("User"))
    host = models.ForeignKey('Host', verbose_name=_("Host"))
    userIdentity = models.ForeignKey('UserIdentity', verbose_name=_("Loged As"))
    blackholeServer = models.CharField(max_length=50,verbose_name=_("BlackHole Server"))
    sourceIP = models.IPAddressField()
    loginDate = models.DateTimeField()
    logoutDate = models.DateTimeField()
    sessionDuration = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_("Session Duration"))
    usage = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_("Session Usage"))
    keyCount = models.IntegerField(verbose_name=_("Session KeyPress Count"))
    logFile = models.CharField(max_length=250,verbose_name=_("Log File"),null=True)
    
    def __unicode__(self):
        return(u"%s[%s] a %s (%s)" % (self.user,
                                      self.userIdentity,
                                      self.host,
                                      self.loginDate))
        
    class Meta(object):
        verbose_name = _("Session Log")
        verbose_name_plural = _("Session Logs")
        ordering = ['loginDate', 'user']
