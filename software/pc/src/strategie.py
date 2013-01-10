from time import sleep
from time import time
from scripts import *

class Strategie:
    def __init__(self, robot, robotChrono,rechercheChemin, config, log, table):

        self.date_debut = time.time()
        

        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.rechercheChemin = rechercheChemin
        self.config = config
        self.log = log
        self.table = table
        self.terminated = False
        
        self.scripts = {"bougies":ScriptBougies, "pipeau":ScriptPipeau}
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.log, self.config)
        
    def boucle_pipeau(self):
#        while not self.terminated :
        while (time.time()-self.date_debut)<self.config["temps_match"]:
            for point_entree in self.liste_points_entree:
                self.robotChrono.temps_action(point_entree)
                self.table.distance_ennemi(point_entree)
                self.table.points(point_entree)
#                note{point_entree}=(calcul de la note en fonction de ce qu'il y a au dessus)
#           on trie note, et on active l'actionneur lié au point d'entrée avec la meilleure note

            self.log.debug("La stratégie a décidé d'aller au point d'entrée: ", (ici le point d'entrée))
            self.log.debug(str(self.robot.get_x())+", "+str(self.robot.get_y())+", "+str(self.robot.get_orientation()))
            sleep(0.1)

    

    def stop(self):
        self.terminated = True	


#TODO
#la méthode temps_action(un point d'entrée) dans le service robotChrono qui renvoie le temps nécessaire à aller à ce point d'entrée et à faire l'action correspondante (pousser les cadeaux, prendre les verre, ...)
#la méthode distance_ennemi(un point d'entrée) dans le service table qui renvoie à un point d'entrée la distance du plus proche obstacle

#dans stratégie:
#la méthode points(un point d'entrée) qui renvoie à un point d'entrée le nombre de points qu'il rapporte
