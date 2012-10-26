#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
#fonction lancée dans le thread de MAJ
from src.thread_MAJ import fonction_MAJ

from time import time,sleep
from math import sqrt,atan,atan2,pi

container = Container()
serie = container.get_service("serie")
robot = container.get_service("robot")

robot.deplacements.set_vitesse_translation(1)
robot.deplacements.set_vitesse_rotation(1)

#thread de mise à jour des coordonnées du robot
thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":container})
thread_MAJ.start()

def affichage() :
    
    debut_timer = time()
    while 346422:
        tab = serie.communiquer("asservissement","?infos", 4)
        
        for ligne in tab:
            if "_" in str(ligne):
                serie.communiquer("asservissement",["?"], 2)
                
        print("PWM ("+str(tab[0])+", "+str(tab[1])+")\t trans : "+str(tab[3])+"\t rot : "+str(tab[2]))
        print("robot : ("+str(robot.x)+", "+str(robot.y)+")\t consigne : ("+str(robot.consigne_x)+", "+str(robot.consigne_y)+")")
        
        #controle de la trajectoire
        if time() - debut_timer > 0.5:
            goto_maj(robot.consigne_x,robot.consigne_y)
            debut_timer = time()
        sleep(0.1)

#thread d'affichage des infos et de controle de la trajectoire
thread_affichage = Thread(None, affichage, None, (), {})
thread_affichage.start()

def goto_maj(x,y):
    delta_x = x-robot.x
    delta_y = y-robot.y
    distance = sqrt(delta_x**2 + delta_y**2)
    if distance > 30:
        if distance < 150:
            #commence par tourner sur lui meme
            goto_init(x,y)
        else:
            ############################
            angle = atan2(delta_y,delta_x)
            ############################
            #if delta_x == 0:
                #if delta_y > 0:
                    #angle = pi/2
                #else:
                    #angle = -pi/2
            #else:
                #angle = atan(delta_y/delta_x)
            #if delta_x < 0:
                #if distance < 150:
                    #distance = -distance
                #elif delta_y > 0:
                    #angle += pi
                #else:
                    #angle -= pi
            ############################
            robot.deplacements.tourner(angle)
            robot.deplacements.avancer(distance)
        
def goto_init(x,y):
    robot.consigne_x = x
    robot.consigne_y = y
    
    
def prompt():
    
    while 37:
        first = input("nb réponses :")
        
        #macros
        nb = 0
        if first == "a":
            goto_init(-200,-200)
        elif first == "z":
            goto_init(-200,0)
        elif first == "q":
            goto_init(0,-200)
        elif first == "s":
            goto_init(0,1)
        """
        else:
            nb = int(first)
            commande = input("@sserv : ")
            reponse = serie.communiquer("asservissement",commande.split(","), nb)
        
        for k in range(nb):
            print(str(reponse[k]))
        """
        sleep(0.1)
        

prompt()