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
#strat.attrib()

serie = container.get_service("serie")