'''
Created on Oct 25, 2012

@author: aenima
'''
from django import forms
from models import User,Host
from django.utils.translation import ugettext_lazy as _

class StatsByUser(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('lastName'), widget=forms.Select(attrs={'class':'span3'}), label=_('User:'))
    from_date = forms.DateField(label=_("From:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
    to_date = forms.DateField(label=_("To:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
    statsTypeChoices = (
                        ('LOGINS_COUNT',_('Logins Count')),
                        ('USAGE',_('Usage')),
                        ('KEY_COUNT',_('Key Count')),
                        ('SOURCE',_('Source')),
                        ('SESSION_DURATION',_('Session Duration')),
                        )
    statsType = forms.ChoiceField(choices=statsTypeChoices,label=_('Stats Type'))

class StatsByHost(forms.Form):
    host = forms.ModelChoiceField(queryset=Host.objects.all().order_by('name'), widget=forms.Select(attrs={'class':'span3'}), label=_('Host:'))
    from_date = forms.DateField(label=_("From:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
    to_date = forms.DateField(label=_("To:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
    statsTypeChoices = (
                        ('LOGINS_COUNT',_('Logins Count')),
                        ('USAGE',_('Usage')),
                        ('KEY_COUNT',_('Key Count')),
                        ('USERS',_('Users')),
                        ('SESSION_DURATION',_('Session Duration')),
                        )
    statsType = forms.ChoiceField(choices=statsTypeChoices,label=_('Stats Type'))    

class FindSessionLogs(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('lastName'), widget=forms.Select(attrs={'class':'span3'}), label=_('User:'))
    from_date = forms.DateField(label=_("From:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
    to_date = forms.DateField(label=_("To:"),
                           widget=forms.widgets.DateInput(format="%d/%m/%Y",attrs={'class':'datePicker'}),
                           input_formats=('%d/%m/%Y',)
                           )
