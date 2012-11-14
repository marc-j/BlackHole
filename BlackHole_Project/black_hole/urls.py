from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^blackhole/', include('black_hole_db.urls')),
)
