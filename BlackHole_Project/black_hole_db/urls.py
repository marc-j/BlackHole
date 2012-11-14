'''
Created on Oct 19, 2012

@author: Nicolas Rebagliati
'''
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as django_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^login/$', django_views.login),
    url(r'^logout/$',django_views.logout,{'next_page': '/backhole/index/'}),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^stats/$', 'black_hole_db.views.stats', name='stats'),
    url(r'^index/$', 'black_hole_db.views.index', name='index'),
    url(r'^listUsers/$', 'black_hole_db.views.listUsers', name='listUsers'),
    url(r'^listHosts/$', 'black_hole_db.views.listHosts', name='listHosts'),
    url(r'^byUser/$', 'black_hole_db.views.byUser', name='byUser'),
    url(r'^byHost/$', 'black_hole_db.views.byHost', name='byHost'),
    url(r'^findSessionLog/$', 'black_hole_db.views.findSessionLog', name='findSessionLog'),
    url(r'^getLog/(?P<log_id>\d+)$', 'black_hole_db.views.get_log', name='getLog'),
)
