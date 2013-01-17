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
        self.points={"cadeau":4*4, "verreNous":6*5, "verreEnnemi": 6*4, "gateau":10*4, "deposer_verre":0}
        self.note={"cadeau":0, "verreNous":0, "verreEnnemi": 0, "gateau":0, "deposer_verre":0}

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.rechercheChemin, self.config, self.log)
        
    def boucle_strategie(self):
        self.log.debug("Stratégie lancée.")
        while not self.timer.fin_match:
            liste_chemin=[]
            for script in self.scripts:
                self.log.debug("Notation de l'action: "+script)
                dureeScript=self.scripts[script].calcule()

#                self.table.RobotAdverseBalise
#                self.table.

                distanceEnnemi=self.table.distance_ennemi(point_entree)

        #point est géré par stratégie
#                note{point_entree}=(calcul de la note en fonction de ce qu'il y a au dessus)
#           on trie note, et on active l'actionneur lié au point d'entrée avec la meilleure note

            self.log.debug("La stratégie a décidé d'aller au point d'entrée")
            if not self.timer.fin_match:
                self.robot.avancer(50)
                script.agit()
#màj point
            sleep(0.1)
        log.debug("Arrêt de la stratégie.")


    
#TODO
#la méthode temps_action(un point d'entrée) dans le service robotChrono qui renvoie le temps nécessaire à aller à ce point d'entrée et à faire l'action correspondante (pousser les cadeaux, prendre les verre, ...)
#la méthode distance_ennemi(un point d'entrée) dans le service table qui renvoie à un point d'entrée la distance du plus proche obstacle

#dans stratégie:
#la méthode points(un point d'entrée) qui renvoie à un point d'entrée le nombre de points qu'il rapporte


