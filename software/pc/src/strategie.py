from time import sleep
from time import time
from math import sqrt
from scripts import *

class Strategie:
    """
    Classe gérant l'intelligence artificielle.
    Son rôle est de noter différents scripts (selon leur durée, la distance d'un ennemi, ...) et de choisir le plus avantageux. C'est également cette classe qui fait les appels d'ajout d'obstacle à la recherche de chemin.
    """
    def __init__(self, robot, robotChrono, hookGenerator, rechercheChemin, table, timer, config, log): #retirer robot

        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log

        self.arguments={"pipeau1":(), "pipeau2":(), "pipeau3":(), "casser_tour":(), "bougies": (1,), "cadeaux1":(0,), "cadeaux2":(1,)}
#        self.scripts = {"cadeaux1": ScriptCadeaux, "cadeaux2":ScriptCadeaux, "bougies":ScriptBougies, "casser_tour":ScriptCasserTour}
        self.scripts = {"bougies":ScriptBougies}
        if not self.config["ennemi_fait_toutes_bougies"]:
            if self.config["ennemi_fait_ses_bougies"]:
                self.scripts["bougies"]=ScriptBougiesRapide
                self.log.warning("On fait les bougies sans détecteur.")
            else:
                self.scripts["bougies"]=ScriptBougies
                self.log.warning("On fait les bougies normalement.")
        else:
            self.log.warning("Puisque l'ennemi est scripté et fait toutes les bougies, on ne les fera pas.")
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]
        self.points={"cadeaux1":0, "cadeaux2":0, "verres": 0, "bougies":0, "deposer_verre":0, "pipeau1":6, "pipeau2": 12, "pipeau3":8, "testHook":0}

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.rechercheChemin, self.config, self.log, self.table)
        
    def boucle_strategie(self):
        """
        Boucle principale de la stratégie. 
        """
        self.log.debug("Stratégie lancée.")

        while not self.timer.get_fin_match():
#            self.rechercheChemin.retirer_obstacles_dynamique();

            note={"cadeaux1":0, "cadeaux2":0, "verreNous":0, "verreEnnemi": 0, "bougies":0, "deposer_verres":0, "pipeau1":0, "pipeau2":0, "pipeau3":0, "casser_tour":0} #les clés sont les scripts

        #        for script in self.points: #retiré pour la durée des tests (tant que les vrais scripts ne sont pas dispo...)
        #            self.points[script]=0
            self.points["deposer_verre"]=6#(nb verre)
            for element in self.table.bougies:
                if not element["traitee"]:
                    self.points["bougies"]+=2 #chaque bougie rapporte 4 points, mais la moitié des bougies sont à l'ennemi...
            for element in self.table.verres:
                if element["present"]:       #à pondérer si l'ascenseur est plutôt plein ou plutôt vide
                    self.points["verres"]+=6 #à tirer vers le haut pour les faire en début de partie (et ensuite baisser les points par incertitude?)
            self.points["cadeaux1"]=0
            for element in self.table.cadeaux:
                if not element["ouvert"]:
                    self.points["cadeaux1"]+=4
            self.points["cadeaux2"]=self.points["cadeaux1"]
            self.points["deposer_verres"]=4*(self.robot.nb_verres_avant+self.robot.nb_verres_arriere)**2 #mettre la vraie valeur
            self.points["casser_tour"]=(time()-self.timer.get_date_debut())

            self.rechercheChemin.preparer_environnement()

            for script in self.scripts:
                if self.points[script]!=0:
                    self.log.debug(script)

                    dureeScript=self.scripts[script].calcule(*self.arguments[script])+1    #au cas où, pour éviter une division par 0... (ce serait vraiment dommage!)
                    if dureeScript<=0:  #si si, c'est déjà arrivé
                        self.log.warning(script+" a un temps d'exécution négatif!")
                        dureeScript=1   #il vaudrait mieux trouver l'origine du bug...

                    distanceE=self._distance_ennemi(script)+1              #idem
                    try:
                        note[script]=1000000000*(self.points[script])/(dureeScript*dureeScript*dureeScript*distanceE*distanceE)
                    except ZeroDivisionError:
                        note[script]=self.points[script]
                        self.log.critical("Division par zéro dans le calcul de la note! :o") #sait-on jamais... je préfère ne pas prendre le risque de voir le robot se paralyser bêtement

                    if script=="verreNous" or script=="verreEnnemi" and dureeScript+deposer_verre.calcule()>(self.config["temps_match"]-time()+self.timer.get_date_debut()): #pour prendre les verres, on ajoute à durée script le temps de déposer les verres
                        self.log.critical("Plus le temps de prendre des verres, on n'aurait pas le temps de les déposer.")
                        ditUneFoisVerre=True
                        note[script]=0
                    elif not dureeScript<(self.config["temps_match"]-time()+self.timer.get_date_debut()): #si on a le temps de faire l'action avant la fin du match
                        self.log.critical("Plus le temps d'exécuter "+script)
                        ditUneFoisAutre=True
                        note[script]=0

                    self.log.debug("Note du script "+script+": "+str(note[script]))

            noteInverse = dict(map(lambda item: (item[1],item[0]),note.items()))
            scriptAFaire=noteInverse[max(noteInverse.keys())]   #ce script a reçu la meilleure note

            self.log.debug("STRATÉGIE FAIT: "+scriptAFaire)
            if not self.timer.get_fin_match():
                self.scripts[scriptAFaire].agit(self.arguments[scriptAFaire])

            sleep(0.1)
        self.log.debug("Arrêt de la stratégie.")

    def _distance_ennemi(self, script): #on prend la distance euclidienne, à vol d'oiseau. Attention, on prend le min: cette valeur est sensible aux mesures aberrantes
        distance_min=3000 #une distance très grande, borne sup de la valeur renvoyée.
        for obstacle in self.table.obstacles():
            delta_x=self.scripts[script].point_entree().x-obstacle.position.x
            delta_y=self.scripts[script].point_entree().y-obstacle.position.y
            d=round(sqrt(delta_x**2 + delta_y**2),2)
            if d<distance_min:
                distance_min=d
        return distance_min

#TODO
#dans robot, il faut le nombre de verres dans chaque ascenseur.
