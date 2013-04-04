
#passage de la couleur
couleur = ""
while couleur != "rouge" and couleur != "bleu":
    couleur = input("Quelle couleur? bleu ou rouge >")
import builtins
builtins.couleur_robot = couleur

#module d'injection de dépendances
from src.container import *
from time import time
from math import pi

ennemi_fait_toutes_bougies = ""
while ennemi_fait_toutes_bougies != "1" and ennemi_fait_toutes_bougies != "0":
    ennemi_fait_toutes_bougies = input("L'ennemi fait-il toutes les bougies? 1 (oui) ou 0 (non) >")

ennemi_fait_ses_bougies = ""
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

#on renseigne au robot sa position
if couleur == "rouge":
    robot.x = 1200
    robot.y = 300
    robot.orientation = pi
else:
    robot.x = -1200
    robot.y = 300
    robot.orientation = 0

#robot.recaler()

# si le jumper est simulé
if "capteurs_actionneurs" in config["cartes_simulation"] or "capteurs_actionneurs" not in config["cartes_serie"]:
    timer = container.get_service("threads.timer")
    input("Jumper simulé")
    timer.date_debut = time()
    timer.match_demarre = True

strategie.boucle_strategie()
