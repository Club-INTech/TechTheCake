#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ
#module de la stratégie (sur le thread principal)
from src.strategie import Strategie

container = Container()
#lancement des services
for service in ["robot", "log", "config"]:
    exec(service+" = container.get_service('"+service+"')")


thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
thread_MAJ.start()

#lancement de la stratégie
strat = Strategie(container)
strat.boucle_pipeau()