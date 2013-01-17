from time import sleep
from scripts import *

class Strategie:
    def __init__(self, robot, robotChrono, hookGenerator, rechercheChemin, table, timer, config, log):

        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log

        self.scripts = {"recalcul":ScriptTestRecalcul}
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]
        self.points={"cadeau":0, "verres": 0, "gateau":0, "deposer_verre":0}
        self.note={"cadeau":0, "verreNous":0, "verreEnnemi": 0, "gateau":0, "deposer_verre":0}

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.rechercheChemin, self.config, self.log)
        
    def boucle_strategie(self):
        self.log.debug("Stratégie lancée.")
        for script in self.points:
            self.points[script]=0
        self.points["deposer_verre"]=6#(nb verre)
        for element in self.table.bougies:
            if not element["traitee"]:
                self.points["gateau"]=self.points["gateau"]+2 #chaque bougie rapporte 4 points, mais la moitié des bougies sont à l'ennemi...
        for element in self.table.verres:
            if element["present"]:
                self.points["verres"]=self.points["verres"]+6
        

        while not self.timer.fin_match:
            for script in self.scripts:
                self.log.debug("Note du script "+script+": "+str(50))
                dureeScript=self.scripts[script].calcule()
                distanceE=self.distance_ennemi()
                
#dans robot, il faut le nombre de verres dans chaque ascenseur. dans config, le nombre de verres max?

#                note{point_entree}=(calcul de la note en fonction de ce qu'il y a au dessus)
#           on trie note, et on active l'actionneur lié au point d'entrée avec la meilleure note
            scriptAFaire="recalcul"

            self.log.debug("La stratégie a décidé d'exécuter le script: "+scriptAFaire)
            if not self.timer.fin_match:
                self.robot.avancer(50)
                self.scripts[scriptAFaire].agit()
#màj point


            sleep(0.1)
        log.debug("Arrêt de la stratégie.")

    def distance_ennemi(self):

#                self.table.RobotAdverseBalise
#                self.table.
        pass
    
#TODO
#la méthode temps_action(un point d'entrée) dans le service robotChrono qui renvoie le temps nécessaire à aller à ce point d'entrée et à faire l'action correspondante (pousser les cadeaux, prendre les verre, ...)
#la méthode distance_ennemi(un point d'entrée) dans le service table qui renvoie à un point d'entrée la distance du plus proche obstacle

#dans stratégie:
#la méthode points(un point d'entrée) qui renvoie à un point d'entrée le nombre de points qu'il rapporte


