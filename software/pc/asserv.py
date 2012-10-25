#module d'injection de dépendances
from src.container import *
#module pour les threads
from threading import Thread
from time import time

container = Container()
serie = container.get_service("serie")

def affichage() :
    debut_timer = time()
    while 346422:
        tab = serie.communiquer("asservissement","?infos", 4)
        
        for ligne in tab:
            if "_" in str(ligne):
                serie.communiquer("asservissement",["?"], 2)
                
        print("PWM ("+str(tab[0])+", "+str(tab[1])+")\t trans : "+str(tab[3])+"\t rot : "+str(tab[2]))
        
        if time() - debut_timer > 2:
            serie.communiquer("asservissement","vp", 0)
            debut_timer = time()

def prompt():
    while 37:
        first = input("nb réponses :")
        
        #macros
        if first == "m":
            nb = 0
            reponse = serie.communiquer("asservissement",["mp"], nb)
        elif first == "a":
            nb = 0
            reponse = serie.communiquer("asservissement",["p",-200,-200], nb)
        elif first == "z":
            nb = 0
            reponse = serie.communiquer("asservissement",["p",-200,0], nb)
        elif first == "q":
            nb = 0
            reponse = serie.communiquer("asservissement",["p",0,-200], nb)
        elif first == "s":
            nb = 0
            reponse = serie.communiquer("asservissement",["p",0,1], nb)
        
        else:
            nb = int(first)
            commande = input("@sserv : ")
            reponse = serie.communiquer("asservissement",commande.split(","), nb)
        
        for k in range(nb):
            print(str(reponse[k]))
        
thread_affichage = Thread(None, affichage, None, (), {})
thread_affichage.start()

prompt()