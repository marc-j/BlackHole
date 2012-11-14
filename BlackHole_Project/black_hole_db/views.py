# Create your views here.
import os
import os, tempfile, zipfile
from datetime import timedelta
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from black_hole_db.models import User, Host
from forms import StatsByUser, FindSessionLogs, StatsByHost
from models import SessionLog
from django.db.models import Avg, Max, Min, Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.utils import json
import simplejson
import qsstats


@login_required
def index(request):
    return render_to_response('blackhole/index.html', context_instance=RequestContext(request))

@login_required
def stats(request):
    pass

@login_required
def listUsers(request):
    users_list = User.objects.all()
    paginator = Paginator(users_list, 35)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    return render_to_response('blackhole/listUsers.html', {'users':users}, context_instance=RequestContext(request))
    
@login_required
def listHosts(request):
    hosts_list = Host.objects.order_by('name')
    paginator = Paginator(hosts_list, 35)
    page = request.GET.get('page')
    try:
        hosts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        hosts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        hosts = paginator.page(paginator.num_pages)
    return render_to_response('blackhole/listHosts.html', {'hosts':hosts}, context_instance=RequestContext(request))


@login_required
def get_log(request, log_id):
    try:
        log = SessionLog.objects.get(id=log_id)
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        archive.write(log.logFile)
        archive.close()
        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=log.zip'
        response['Content-Length'] = temp.tell()
        temp.seek(0)
        return response
    except Exception as e:
        return HttpResponse("<p>Unknown File %s</p>" % e)
    

@login_required
def findSessionLog(request):
    if request.method == 'POST':
        form = FindSessionLogs(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            info = {'user':user, 'from':from_date, 'to':to_date}
            days = timedelta(days=1)
            logs = SessionLog.objects.filter(loginDate__range=(from_date, to_date + days), user=user)
            for log in logs:
                if log.logFile:
                    if os.path.isfile(log.logFile):
                        log.canDownload = True
                    else:
                        log.canDownload = False
                else:
                    log.canDownload = False
            return render_to_response('blackhole/findSessionLog.html', {'info':info, 'logs':logs}, context_instance=RequestContext(request))
    else:
        form = FindSessionLogs()
    return render_to_response('blackhole/findSessionLog.html', {'form':form}, context_instance=RequestContext(request))
    
# Stats Views
@login_required
def byUser(request):
    if request.method == 'POST':
        form = StatsByUser(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            oneDayAhead = timedelta(days=1)
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date') + oneDayAhead
            statsType = form.cleaned_data.get('statsType')
            info = {'user':user, 'from':from_date, 'to':to_date}
            if statsType == 'SOURCE':
                data = SessionLog.objects.filter(loginDate__range=(from_date, to_date), user=user).values('sourceIP').annotate(total=Count('user'))
                return render_to_response('blackhole/statsSource.html', {'data': data, 'info':info}, context_instance=RequestContext(request))
            elif statsType == 'LOGINS_COUNT':
                logins = SessionLog.objects.filter(loginDate__range=(from_date, to_date), user=user)
                qss = qsstats.QuerySetStats(logins, 'loginDate')
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date, value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000, value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsLogins.html', {'data': data, 'info':info}, context_instance=RequestContext(request))
            elif statsType == 'SESSION_DURATION':
                logins = SessionLog.objects.filter(loginDate__range=(from_date, to_date), user=user)
                qss = qsstats.QuerySetStats(logins, 'loginDate', Sum('sessionDuration'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date, value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000, value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsSessionDuration.html', {'data': data, 'info':info}, context_instance=RequestContext(request))
            elif statsType == 'KEY_COUNT':
                logins = SessionLog.objects.filter(loginDate__range=(from_date, to_date), user=user)
                qss = qsstats.QuerySetStats(logins, 'loginDate', Sum('keyCount'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date, value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000, value))
                data = json.dumps(logsData)
                return render_to_response('blackhole/statsKeyCount.html', {'data': data, 'info':info}, context_instance=RequestContext(request))
            elif statsType == 'USAGE':
                logins = SessionLog.objects.filter(loginDate__range=(from_date, to_date), user=user)
                qss = qsstats.QuerySetStats(logins, 'loginDate', Sum('usage'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date, value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000, value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsUsage.html', {'data': data, 'info':info}, context_instance=RequestContext(request))
    else:
        form = StatsByUser()
    return render_to_response('blackhole/byUser.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def byHost(request):
    if request.method == 'POST':
        form = StatsByHost(request.POST)
        if form.is_valid():
            oneDayAhead = timedelta(days=1)
            host = form.cleaned_data.get('host')
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date') + oneDayAhead
            statsType = form.cleaned_data.get('statsType')
            info = {'host':host,'from':from_date,'to':to_date}
            if statsType == 'USERS':
                data =  SessionLog.objects.filter(loginDate__range=(from_date,to_date),host=host).values('user').annotate(total=Count('user'))
                return render_to_response('blackhole/statsHostUsers.html',{'data': data,'info':info}, context_instance=RequestContext(request))
            elif statsType == 'LOGINS_COUNT':
                logins = SessionLog.objects.filter(loginDate__range=(from_date,to_date),host=host)
                qss = qsstats.QuerySetStats(logins, 'loginDate')
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date,value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000,value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsHostLogins.html',{'data': data,'info':info}, context_instance=RequestContext(request))
            elif statsType =='SESSION_DURATION':
                logins = SessionLog.objects.filter(loginDate__range=(from_date,to_date),host=host)
                qss = qsstats.QuerySetStats(logins, 'loginDate',Sum('sessionDuration'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date,value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000,value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsHostSessionDuration.html',{'data': data,'info':info}, context_instance=RequestContext(request))
            elif statsType =='KEY_COUNT':
                logins = SessionLog.objects.filter(loginDate__range=(from_date,to_date),host=host)
                qss = qsstats.QuerySetStats(logins, 'loginDate',Sum('keyCount'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date,value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000,value))
                data = simplejson.dumps(logsData, use_decimal=True)
                return render_to_response('blackhole/statsHostKeyCount.html',{'data': data,'info':info}, context_instance=RequestContext(request))
            elif statsType =='USAGE':
                logins = SessionLog.objects.filter(loginDate__range=(from_date,to_date),host=host)
                qss = qsstats.QuerySetStats(logins, 'loginDate',Sum('usage'))
                time_series = qss.time_series(from_date, to_date)
                logsData = []
                for date,value in time_series:
                    logsData.append((int(date.strftime("%s")) * 1000,value))
                data = simplejson.dumps(logsData)
                return render_to_response('blackhole/statsHostUsage.html',{'data': data,'info':info}, context_instance=RequestContext(request))
    else:
        form = StatsByHost()
    return render_to_response('blackhole/byHost.html',{'form':form}, context_instance=RequestContext(request))
    
   
