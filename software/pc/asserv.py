#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ

from time import time,sleep
from math import sqrt,atan,atan2,pi

container = Container()
robot = container.get_service("robot")

#thread de mise à jour des coordonnées du robot
thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
thread_MAJ.start()

"""
serie = container.get_service("serie")
def affichage() :
    while 346422:
        tab = serie.communiquer("asservissement","?infos", 4)
        
        for ligne in tab:
            if "_" in str(ligne):
                serie.communiquer("asservissement",["?"], 2)
                
        print("PWM ("+str(tab[0])+", "+str(tab[1])+")\t trans : "+str(tab[3])+"\t rot : "+str(tab[2]))
        print("robot : ("+str(robot.x)+", "+str(robot.y)+")\t consigne : ("+str(robot.consigne_x)+", "+str(robot.consigne_y)+")")
        sleep(0.1)

#thread d'affichage des infos et de controle de la trajectoire
#thread_affichage = Thread(None, affichage, None, (), {})
#thread_affichage.start()
"""

#@ test
def prompt():
    
    while 37:
        first = input("nb réponses :")
        
        #macros
        nb = 0
        
        #serie
        #if first == "a":
            #robot.va_au_point(-200,-200)
        #elif first == "z":
            #robot.va_au_point(-200,0)
        #elif first == "q":
            #robot.va_au_point(0,-200)
        #elif first == "s":
            #robot.va_au_point(0,1)
            
        #simulateur
        if first == "a":
            robot.deplacements.simulateur.drawPoint(-1000,800,"red",False)
            robot.va_au_point(-1000,800)
        elif first == "z":
            robot.deplacements.simulateur.drawPoint(-500,800,"red",False)
            robot.va_au_point(-500,800)
        elif first == "q":
            robot.deplacements.simulateur.drawPoint(-1000,300,"red",False)
            robot.va_au_point(-1000,300)
        elif first == "s":
            robot.deplacements.simulateur.drawPoint(-500,300,"red",False)
            robot.va_au_point(-500,300)
        """
        else:
            nb = int(first)
            commande = input("@sserv : ")
            reponse = serie.communiquer("asservissement",commande.split(","), nb)
        
        for k in range(nb):
            print(str(reponse[k]))
        """
        sleep(0.1)
        
robot.deplacements.set_vitesse_translation(1)
robot.deplacements.set_vitesse_rotation(1)
prompt()