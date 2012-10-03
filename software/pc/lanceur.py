#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread

#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ

container = Container()
#lancement des services
for service in ["Robot", "Log"]:#, Table, Capteurs]
    exec(service+" = container.get_service("+service+")")



#TODO thread_MAJ nécessite : robot, table, capteurs, actionneurs, log, config

thread_MAJ = Thread(None, fonction_MAJ, None, (), {"robot":Robot,"log":Log})
thread_MAJ.start()

from time import sleep
while 1 :
    Log.debug("_________")
    sleep(0.2)