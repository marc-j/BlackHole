'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender(object):
    '''
    classdocs
    '''


    def __init__(self,user,token,sessionID):
        '''
        Constructor
        '''
        sender = "xxxx@xxxx"
        destination = user.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Bastion Token"
        msg['From'] = sender
        msg['To'] = destination
        html = """\
        <html>
        <head></head>
        <body>
        <p>Solicitud de Token para Ingreso a Produccion Altamira Argentina<br>
        Para la sesion %s su Token es: %s<br>
        </p>
        </body>
        </html>
        """ % (sessionID,token)
        htmlMessage = MIMEText(html, 'html')
        msg.attach(htmlMessage)
        s = smtplib.SMTP('0.0.0.0')
        s.sendmail(sender, destination, msg.as_string())
        s.quit()
