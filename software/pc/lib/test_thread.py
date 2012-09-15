# -*- coding: utf-8 -*-
import threading
import asservissement
from time import sleep

asserv = asservissement.Asservissement()

def boucle_acquittement():
    while 42:
        asserv.gestion_stoppage()
        print asserv.acquittement()
        print "####"
        
def reste_du_code():
    while 42:
        print "yaya"
        sleep(0.5)
        
thread_acquittement = threading.Thread(None, boucle_acquittement, None, (), {})
thread_reste_du_code = threading.Thread(None, reste_du_code, None, (), {})

thread_acquittement.start()
thread_reste_du_code.start()