#module d'injection de dépendances
import time
from src.container import *
container = Container()
import math
from src.outils_maths.point import Point

#module de la stratégie
robot = container.get_service("robot")
config = container.get_service("config")
scripts = container.get_service("scripts")
timer = container.get_service("threads.timer")
strategie = container.get_service("strategie")
table = container.get_service("table")
rechercheChemin = container.get_service("rechercheChemin")

if config["couleur"] == "rouge":
    robot.x = 1220
    robot.y = 400
    robot.orientation = math.pi
    version_cadeaux = 1
else:
    robot.x = -1220
    robot.y = 400
    robot.orientation = 0
    version_cadeaux = 0
    
robot.recaler()

while not timer.match_demarre:
    time.sleep(.5)

try:
    #cadeaux
    scripts["ScriptCadeaux"].versions()
    scripts["ScriptCadeaux"].agit(version_cadeaux)
except:
    print("ca chie, on enchaine...")
    
try:
    #verres
    robot.effectuer_symetrie = True
    robot.set_vitesse_translation(65)

    robot.marche_arriere = False
    
    ##si verres au début !
    #robot.va_au_point(Point(800,300))
    #robot.va_au_point(Point(-100,300))

    robot.va_au_point(Point(-200,550))
    robot.va_au_point(Point(1040,550),retenter_si_blocage=False, sans_lever_exception=True)

    robot.marche_arriere = True
    robot.va_au_point(Point(-100,550))
    robot.marche_arriere = False
    robot.va_au_point(Point(-100,800))
    robot.va_au_point(Point(1040,800),retenter_si_blocage=False, sans_lever_exception=True)

    robot.marche_arriere = True
    robot.va_au_point(Point(-100,800))
    robot.marche_arriere = False
    robot.va_au_point(Point(-100,1050))
    robot.va_au_point(Point(1040,1050),retenter_si_blocage=False, sans_lever_exception=True)

    robot.marche_arriere = True
    robot.va_au_point(Point(0,1050))

except:
    print("ca chie, on enchaine...")
