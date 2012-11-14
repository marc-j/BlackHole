# -*- coding: utf-8 -*-
from django.contrib import admin
from black_hole_db.models import *
import os
import string
import random
import pwd
from django.utils.translation import ugettext_lazy as _

class PrivateKeyAdmin(admin.ModelAdmin):
    list_display = ('user','type','environment')
    search_fields = ['user']
    list_filter = ('user','environment')
    ordering = ['environment','user']
    
class UserAdmin(admin.ModelAdmin):
    actions = ['disable_users','enable_users']
    list_display = ('userName','lastName','name','profile','enable','lastLogin')
    search_fields = ['userName','profile__name']
    list_filter = ('enable','profile')
    filter_horizontal = ('allowedByEnvironments',)
    ordering = ['profile__name','userName']
    #exclude  = ('logEnable','timeEnabled','timeFrom','timeTo',)
    
    def disable_users(self,request,queryset):
        queryset.update(enable = False)
    disable_users.short_description = _("Disable selected users")

    def enable_users(self,request,queryset):
        queryset.update(enable = True)
    enable_users.short_description = _("Enable selected users")
      
class EnvironmentAdmin(admin.ModelAdmin):
    search_fields = ['description']

class HostConnectionAdmin(admin.ModelAdmin):
    list_display = ('host','userAuthentication')
    list_filter = ('userAuthentication','host__environment',)
    search_fields = ['host__name']

class HostAdmin(admin.ModelAdmin):
    list_display = ('name','environment','description','ip','os')
    search_fields = ['name','ip']
    list_filter = ('environment',)
    ordering = ['environment']

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name']
    filter_vertical = ('hosts',)
    ordering = ['name']

class UserIdentityAdmin(admin.ModelAdmin):
    search_fields = ['username']
    ordering = ['username']
    
admin.site.register(Host,HostAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(Environment,EnvironmentAdmin)
admin.site.register(UserIdentity,UserIdentityAdmin)
admin.site.register(HostConnection,HostConnectionAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(PrivateKey,PrivateKeyAdmin)
admin.site.register(SessionLog)


