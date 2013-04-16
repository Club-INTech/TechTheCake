
#passage de la couleur
#couleur = ""
couleur = "rouge"
while couleur != "rouge" and couleur != "bleu":
    couleur = input("Quelle couleur? bleu ou rouge >")
import builtins
builtins.couleur_robot = couleur

#module d'injection de dépendances
from src.container import *
from time import time
from math import pi
from outils_maths.point import Point

ennemi_fait_toutes_bougies = "0"
#ennemi_fait_toutes_bougies = ""
while ennemi_fait_toutes_bougies != "1" and ennemi_fait_toutes_bougies != "0":
    ennemi_fait_toutes_bougies = input("L'ennemi fait-il toutes les bougies? 1 (oui) ou 0 (non) >")

if ennemi_fait_toutes_bougies == "1":
    ennemi_fait_ses_bougies = "1"
else:
#    ennemi_fait_ses_bougies = ""
    ennemi_fait_ses_bougies = "0"
    while ennemi_fait_ses_bougies != "1" and ennemi_fait_ses_bougies != "0":
        ennemi_fait_ses_bougies = input("L'ennemi fait-il ses bougies à lui? 1 (oui) ou 0 (non) >")
    
container = Container()

#module de la stratégie
config = container.get_service("config")
config["couleur"] = couleur
config["ennemi_fait_toutes_bougies"] = bool(int(ennemi_fait_toutes_bougies))
config["ennemi_fait_ses_bougies"] = bool(int(ennemi_fait_ses_bougies))
strategie = container.get_service("strategie")
robot = container.get_service("robot")
log = container.get_service("log")

#on renseigne au robot sa position
depart = Point(1350,400*(config["case_depart_principal"]-0.5))

if config["couleur"] == "rouge":
    robot.x = depart.x
    robot.y = depart.y
    robot.orientation = pi
else:
    robot.x = -depart.x
    robot.y = depart.y
    robot.orientation = 0

robot.set_vitesse_translation(2)
robot.set_vitesse_rotation(2)

if config["cartes_simulation"]==[]:
    simulateur = container.get_service("simulateur")
    simulateur.setRobotPosition(robot.x, robot.y)

#robot.recaler()

# si le jumper est simulé
if "capteurs_actionneurs" in config["cartes_simulation"] or "capteurs_actionneurs" not in config["cartes_serie"]:
    timer = container.get_service("threads.timer")
    input("Jumper simulé")
    timer.date_debut = time()
    timer.match_demarre = True
else:
    log.debug("Prêt pour le jumper!")

    timer = container.get_service("threads.timer")
    input("Jumper simulé")
    timer.date_debut = time()
    timer.match_demarre = True


#On se décolle du bord
strategie.boucle_strategie()

