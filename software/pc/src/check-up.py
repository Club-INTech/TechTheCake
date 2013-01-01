"""
Procédure de CHECK-UP rapide (avant match)
La majorité des fonctionnalités du robot sont testées de facon unitaire,
après l'affichage du test via un prompt.
"""

#module d'injection de dépendances
from container import *

from threading import Thread,Event
from time import sleep
from math import pi

container = Container()
log = container.get_service("log")
robot = container.get_service("robot")

print("##############################")
print("### tests des deplacements ###")
print("##############################")

posX = robot.x
posY = robot.y
orient = robot.orientation
log.debug("# Robot positionné à ("+str(posX)+", "+str(posY)+") et orienté vers "+str(orient)+".")

input("\n# test de rotation\n")
log.debug("")
robot.tourner(3*pi/4)

input("\n# test de translation\n")
robot.avancer(354)

input("\n# test de va_au_point\n")
robot.va_au_point(posX - 500,posY)

input("\n# va_au_point retour\n")
robot.va_au_point(posX,posY)
robot.tourner(pi)

input("\n# test d'arret\n")
avancer = Thread(None, robot.avancer, None, (), {"distance":1500})
avancer.start()

input("\n# appuyez sur entrée pour stopper le robot\n")
robot.stopper()

print("##########################")
print("### tests des vitesses ###")
print("##########################")

input("\n# tests des vitesses de translation\n")

input("\n# 1ère vitesse en translation\n")
robot.set_vitesse_translation(1)
robot.avancer(700)
robot.marche_arriere = True
robot.avancer(-700)
robot.marche_arriere = False

input("\n# 2ème vitesse en translation\n")
robot.set_vitesse_translation(2)
robot.avancer(700)
robot.marche_arriere = True
robot.avancer(-700)
robot.marche_arriere = False

input("\n# 3ème vitesse en translation\n")
robot.set_vitesse_translation(3)
robot.avancer(700)
robot.marche_arriere = True
robot.avancer(-700)
robot.marche_arriere = False

input("\n# tests des vitesses de rotation\n")
robot.set_vitesse_translation(2)
robot.tourner(0)

input("\n# 1ère vitesse en rotation\n")
robot.set_vitesse_rotation(1)
robot.tourner(3*pi/4)
robot.tourner(0)

input("\n# 2ème vitesse en rotation\n")
robot.set_vitesse_rotation(2)
robot.tourner(3*pi/4)
robot.tourner(0)

input("\n# 3ème vitesse en rotation\n")
robot.set_vitesse_rotation(3)
robot.tourner(3*pi/4)
robot.tourner(0)

print("##########################")
print("### tests des capteurs ###")
print("##########################")

input("\n# tests de la distance renvoyée par les capteurs de proximité\n")
def fonction_mesure(event):
    while (not event.is_set()):
        print(robot.capteurs.mesurer())
        event.wait(0.5)
fin_mesure = Event()
mesurer = Thread(None, fonction_mesure, None, (), {"event":fin_mesure})
mesurer.start()

input("\n# appuyez sur entrée pour stopper la mesure\n")
fin_mesure.set()

print("#############################")
print("### tests des actionneurs ###")
print("#############################")

input("\n# test d'ouverture de l'actionneur cadeaux\n")
robot.actionneurs.ouvrir_cadeau()

input("\n# test de fermeture de l'actionneur cadeaux\n")
robot.actionneurs.fermer_cadeau()

#TODO actionneurs à compléter...