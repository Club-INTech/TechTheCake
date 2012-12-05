#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ
#module de la stratégie (sur le thread principal)
from src.strategie import Strategie

container = Container()

#lancement du thread de mise à jour des coordonnées
config = container.get_service("config")
if config["mode_simulateur"]:
    #si on est en mode simulateur...
    thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
    thread_MAJ.start()
else:
    #...ou si l'asservissement en série est présent
    serie = container.get_service("serie")
    if hasattr(serie.peripheriques["asservissement"],'serie'):
        thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
        thread_MAJ.start()

##############################
#codes de test :
from time import sleep

#strat = Strategie(container)
#strat.robot.recaler()
#strat.scripts["pipeau"].agit()

#robot = container.get_service("robot")
#robot.recaler()