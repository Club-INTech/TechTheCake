#module d'injection de dépendances
from src.container import *
container = Container()
import math
from src.outils_maths.point import Point

#module de la stratégie
robot = container.get_service("robot")
capteurs = container.get_service("capteurs")
log = container.get_service("log")

import time

while not robot.pret:
    time.sleep(0.1)
    
time.sleep(1)


robot.orientation = 0
#robot.x = 1377
#robot.y = 945
robot.x = -1220
robot.y = 1300


robot.deplacements.set_vitesse_rotation(120)
robot.deplacements.set_vitesse_translation(120)

print("            ~~###~~ bienvenue dans la console $0p@1!z7 ~~###~~")
print("exit pour sortir |  r pour vitesse rotation | t pour vitesse translation")
print("avancer avec u -> p   | reculer avec j -> m | orienter avec z,q,s,d ")
last = "99"

while 1:
    try:
        ordre = input("?")
        if ordre == "":
            ordre = last
        if ordre == "exit":
            break
        elif ordre == "r":
            robot.deplacements.set_vitesse_rotation(int(input()))
        elif ordre == "t":
            robot.deplacements.set_vitesse_translation(int(input()))
            
        elif ordre == "u":
            robot.avancer(100)
        elif ordre == "i":
            robot.avancer(300)
        elif ordre == "o":
            robot.avancer(500)
        elif ordre == "p":
            robot.avancer(1000)
            
        elif ordre == "j":
            robot.avancer(-100)
        elif ordre == "k":
            robot.avancer(-300)
        elif ordre == "l":
            robot.avancer(-500)
        elif ordre == "m":
            robot.avancer(-1000)
            
        elif ordre == "z":
            robot.tourner(math.pi)
        elif ordre == "q":
            robot.tourner(-math.pi/2)
        elif ordre == "s":
            robot.tourner(0)
        elif ordre == "d":
            robot.tourner(math.pi/2)
            
        
        elif ordre == "w":
            print(capteurs.serie.communiquer("capteurs_actionneurs",["us_av"],1)[0])
        elif ordre == "x":
            print(robot.capteurs.serie.communiquer("capteurs_actionneurs",["ir_av"],1)[0])
        elif ordre == "c":
            print(capteurs.mesurer(False))
            
        elif ordre == "ww":
            print(capteurs.serie.communiquer("capteurs_actionneurs",["us_arr"],1)[0])
        elif ordre == "xx":
            print(robot.capteurs.serie.communiquer("capteurs_actionneurs",["ir_arr"],1)[0])
        elif ordre == "cc":
            print(capteurs.mesurer(True))
            
        elif ordre == "haut":
            robot.altitude_ascenseur(True, "haut")
            robot.altitude_ascenseur(False, "haut")
        elif ordre == "bas":
            robot.altitude_ascenseur(True, "bas")
            robot.altitude_ascenseur(False, "bas")
            
        elif ordre == "ouvre":
            robot.actionneurs_ascenseur(True, "ouvert")
            robot.actionneurs_ascenseur(False, "ouvert")
        elif ordre == "oouvre":
            robot.actionneurs_ascenseur(True, "petit ouvert")
            robot.actionneurs_ascenseur(False, "petit ouvert")
        elif ordre == "ferme":
            robot.actionneurs_ascenseur(True, "ferme")
            robot.actionneurs_ascenseur(False, "ferme")
        elif ordre == "fferme":
            robot.actionneurs_ascenseur(True, "ferme_completement")
            robot.actionneurs_ascenseur(False, "ferme_completement")
            
        elif ordre == "xy":
            print(robot.x,robot.y)
            
        elif ordre == "des":
            robot.deplacements.serie.communiquer("asservissement",["cr0"],0)
            robot.deplacements.serie.communiquer("asservissement",["ct0"],0)
            
        elif ordre == "v":
            robot.va_au_point(Point(-700,200), trajectoire_courbe=False)
        elif ordre == "b":
            robot.va_au_point(Point(1220,400), trajectoire_courbe=False)
            robot.tourner(math.pi)
            
        elif ordre == "ballon":
            robot.actionneurs.gonfler_ballon(False)
            
        elif ordre == "bougies":
            while 1:
                bougie = input("h[1,2,3], b[1,2,3], q ?")
                if bougie == "h1":
                    robot.actionneurs.actionneurs_bougie(True, "haut")
                elif bougie == "h2":
                    robot.actionneurs.actionneurs_bougie(True, "moyen")
                elif bougie == "h3":
                    robot.actionneurs.actionneurs_bougie(True, "bas")
                elif bougie == "b1":
                    robot.actionneurs.actionneurs_bougie(False, "haut")
                elif bougie == "b2":
                    robot.actionneurs.actionneurs_bougie(False, "moyen")
                elif bougie == "b3":
                    robot.actionneurs.actionneurs_bougie(False, "bas")
                elif bougie == "q" or "exit":
                    break
        elif ordre == "flush":
            log.flush()
        elif ordre == "log":
            log.warning("azezae")
            
        last = ordre
    except:
        pass