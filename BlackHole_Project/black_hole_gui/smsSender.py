'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
import smpplib

class SMSSender(object):
    def __init__(self,user,token,sessionID):
        '''
        Constructor
        '''
        if user.celular == '':
            #El usuario tiene para generar token pero no tiene celular cargado
            raise Exception("No celuclar phone number for this user")
        sender = '00541153212952'
        destination = user.celular
        msg = 'Para la sesion %s su Token es: %s' % (sessionID,token)
        tonA = 1
        npiA = 1
        tonB = 0
        npiB = 1
        server = '0.0.0.0'
        port = 5020
        system_id = "xxxxxxxxxx"
        password = "xxxxxxxx"
        system_type = "xxxxxxxxx"
        try:
            client = smpplib.client.Client(server, port)
            client.connect()
            client.bind_transmitter(system_id=system_id,password=password, system_type=system_type)
            client.send_message(source_addr_ton = tonA,
                                source_addr_npi = npiA,
                                source_addr = sender,
                                dest_addr_ton = tonB,
                                dest_addr_npi = npiB,
                                destination_addr= destination,
                                short_message = msg)
        except Exception as e:
            raise e
