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



strat = Strategie(container)

#input("appuyer sur une touche pour lancer le calcul de durée du script...")
#print(strat.scripts["pipeau"].calcule())
#input("appuyer sur une touche pour effectuer les mouvements du script...")
#strat.scripts["pipeau"].agit()

strat.robot.recaler()