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
from math import pi
robot = container.get_service("robot")
#attente de la mise à jour des coordonnées
while not robot.y:
    sleep(0.1)
    
robot.marche_arriere = True
robot.couleur = "rouge"

robot.gestion_va_au_point(-800,700)
robot.gestion_tourner(pi/4)
robot.gestion_avancer(500)

#robot.gestion_va_au_point(400,500)

#input("appuyer sur une touche pour lancer le calcul de durée du script...")
#print(strat.scripts["pipeau"].calcule())
#input("appuyer sur une touche pour effectuer les mouvements du script...")
#strat.scripts["pipeau"].agit()

#from time import sleep
#while 42:
    #print("("+str(strat.robot.x)+", "+str(strat.robot.y)+")")
    #sleep(0.2)
