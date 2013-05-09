import time
import sys
import math
from src.container import *
from outils_maths.point import Point

container = Container()

strategie = container.get_service("strategie")
robot = container.get_service("robot")
config = container.get_service("config")
log = container.get_service("log")
timer = container.get_service("threads.timer")

# Affichage des paramètres avant lancement
print("")
print("Vérification des paramètres:")
print("----------------------------")

print("Couleur du robot:\t\t\t", config["couleur"])
print("Case départ du robot principal:\t\t", config["case_depart_principal"])
print("Phases finales:\t\t\t\t", config["phases_finales"])
print("L'ennemi fait toutes les bougies:\t", config["ennemi_fait_toutes_bougies"])

input("\n\tVérification humaine requise pour continuer.")

#on renseigne au robot sa position
depart = Point(1350,400*(config["case_depart_principal"]-0.5))

if config["couleur"] == "rouge":
    robot.x = depart.x
    robot.y = depart.y
    robot.orientation = math.pi
else:
    robot.x = -depart.x
    robot.y = depart.y
    robot.orientation = 0

#Toujours mettre un sleep après avoir affecté les variables robot.x ou robot.y (?)
time.sleep(1)

# Recalage si série
#if "capteurs_actionneurs" in config["cartes_serie"]:
robot.initialiser_actionneurs()
robot.recaler()

# Lancement du match si les capteurs sont simulés
if "capteurs_actionneurs" in config["cartes_simulation"]:
    timer.match_demarre = True
    

strategie.boucle_strategie()

