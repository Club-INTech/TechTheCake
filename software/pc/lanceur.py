#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ
#module de la stratégie (sur le thread principal)
from src.strategie import Strategie

container = Container()

thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
thread_MAJ.start()

#strat = Strategie(container)
#strat.robot.recaler()
#strat.scripts["pipeau"].agit()

from time import sleep
robot = container.get_service("robot")
#attente de la mise à jour des coordonnées
while not robot.y:
    sleep(0.1)

    
# Do what the fuck you want
robot.recaler()