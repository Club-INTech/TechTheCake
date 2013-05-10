#module d'injection de dépendances
from src.container import *
container = Container()

import builtins
import math
import time
from src.outils_maths.point import Point

config = container.get_service("config")
scripts = container.get_service("scripts")
strategie = container.get_service("strategie")
robot = container.get_service("robot")
table = container.get_service("table")
rechercheChemin = container.get_service("rechercheChemin")
timer = container.get_service("threads.timer")

time.sleep(2)
if config["couleur"] == "bleu":
    robot.orientation = 0
    robot.x = -1377
    robot.y = 1429
else:
    robot.orientation = math.pi
    robot.x = 1377
time.sleep(3)

robot.marche_arriere = False
robot.set_vitesse_translation("entre_scripts")
robot.set_vitesse_rotation("entre_scripts")

robot.avancer(300)

time.sleep(2)
input()

#strategie.boucle_strategie()
    
rechercheChemin.retirer_obstacles_dynamiques()
rechercheChemin.charge_obstacles(avec_verres_entrees=False)
rechercheChemin.prepare_environnement_pour_visilibity()

#scripts["ScriptRecupererVerresZoneRouge"].versions()
#scripts["ScriptRecupererVerresZoneRouge"].agit(0)

#scripts["ScriptRecupererVerresZoneBleu"].versions()
#scripts["ScriptRecupererVerresZoneBleu"].agit(0)

#scripts["ScriptBougies"].versions()
#scripts["ScriptBougies"].agit(0)

scripts["ScriptCadeaux"].versions()
scripts["ScriptCadeaux"].agit(0)
