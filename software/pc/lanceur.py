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
config = container.get_service("config")
#attente de la mise à jour des coordonnées
while not robot.y:
    sleep(0.1)
    
robot.marche_arriere = False
robot.couleur = "bleu"

xM = -200
yM = 1000
xA = 500
yA = 350
pas = 100
if config["mode_simulateur"]:
    affiche_xA = xA
    affiche_xM = xM
    if robot.couleur == "bleu":
        affiche_xA *= -1
        affiche_xM *= -1
    robot.deplacements.simulateur.drawPoint(affiche_xA,yA,"red",True)
    robot.deplacements.simulateur.drawPoint(affiche_xM,yM,"black",True)
else:
    robot.x = 1170
    robot.y = 250
    robot.orientation = pi

#robot.recaler()
#print(robot.va_au_point(0,500))
#input()
print(robot.gestion_va_au_point(xA,yA))
input()
print(robot.gestion_arc_de_cercle(xM,yM,pas))
    


#input("appuyer sur une touche pour lancer le calcul de durée du script...")
#print(strat.scripts["pipeau"].calcule())
#input("appuyer sur une touche pour effectuer les mouvements du script...")
#strat.scripts["pipeau"].agit()

#from time import sleep
#while 42:
    #print("("+str(strat.robot.x)+", "+str(strat.robot.y)+")")
    #sleep(0.2)
