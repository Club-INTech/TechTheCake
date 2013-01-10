from time import sleep
from scripts import *

class Strategie:
    def __init__(self, robot, robotChrono, hookGenerator, rechercheChemin, config, log, table, timer):

        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.rechercheChemin = rechercheChemin
        self.config = config
        self.hookGenerator=hookGenerator
        self.log = log
        self.table = table
        self.timer = timer
        
        self.scripts = {"bougies":ScriptBougies, "pipeau":ScriptTestHooks}
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.log, self.config)
        
    def boucle_pipeau(self):
        while not timer.fin_match:
            liste_chemin=[]
            for script in self.scripts:
                dureeScript=script.calcule()
                distanceEnnemi=self.table.distance_ennemi(point_entree)

        #point est géré par stratégie
#                note{point_entree}=(calcul de la note en fonction de ce qu'il y a au dessus)
#           on trie note, et on active l'actionneur lié au point d'entrée avec la meilleure note

            self.log.debug("La stratégie a décidé d'aller au point d'entrée: ")
            self.log.debug(str(self.robot.get_x())+", "+str(self.robot.get_y())+", "+str(self.robot.get_orientation()))
            script.agit()
            sleep(0.1)

    
#TODO
#la méthode temps_action(un point d'entrée) dans le service robotChrono qui renvoie le temps nécessaire à aller à ce point d'entrée et à faire l'action correspondante (pousser les cadeaux, prendre les verre, ...)
#la méthode distance_ennemi(un point d'entrée) dans le service table qui renvoie à un point d'entrée la distance du plus proche obstacle

#dans stratégie:
#la méthode points(un point d'entrée) qui renvoie à un point d'entrée le nombre de points qu'il rapporte


