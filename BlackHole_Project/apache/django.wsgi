import os, sys
sys.path.append('/home/BlackHole/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'black_hole.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
