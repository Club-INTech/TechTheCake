import threading
from mutex import Mutex
from outils_maths.point import Point
from outils_maths.vitesse import Vitesse
from math import cos,sin,pi
from time import sleep,time
import socket
from random import randint

class AbstractThread(threading.Thread):
    
    stop_threads = False
    
    def __init__(self, container):
        threading.Thread.__init__(self)
        self.container = container
        
class ThreadPosition(AbstractThread):
    
    def __init__(self, container):
        AbstractThread.__init__(self, container)
        
    def run(self):
        log = self.container.get_service("log")
        robot = self.container.get_service("robot")
        timer = self.container.get_service("threads.timer")
        
        log.debug("lancement du thread de mise à jour")
        
        #le reste du code attend une première mise à jour des coordonnées
        robot_pret = False
        
        while not robot_pret:
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread de mise à jour")
                return None
            try:
                robot.update_x_y_orientation()
                robot_pret = True
            except Exception as e:
                print(e)
            sleep(0.1)
            
        robot.pret = True
        
        while not timer.get_fin_match():
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread de mise à jour")
                return None
        
            #mise à jour des coordonnées dans robot
            try:
                robot.update_x_y_orientation()
            except Exception as e:
                print(e)
            sleep(0.1)
            
        log.debug("Fin du thread de mise à jour")

class ThreadTimer(AbstractThread):
    """
    Classe de gestion du temps et d'appels réguliers.
    Deux variables globales sont très utilisées: timer.fin_match et timer.match_demarre. 
    Supprime les obstacles périssables du service de table.
    """
    def __init__(self, log, config, robot, com2principal):
        AbstractThread.__init__(self, None)
        self.log = log
        self.config = config
        self.robot = robot
        self.com2principal = com2principal
        
        self.match_demarre = False
        self.fin_match = False
        self.mutex = Mutex()
        self.compte_rebours = True

    def initialisation(self):
        """
        Boucle qui attend le début du match et qui modifie alors la variable timer.match_demarre
        """
        while not self.com2principal.demarrage_match():
            if AbstractThread.stop_threads:
                self.log.debug("Stoppage du thread timer")
                return None
            sleep(.5)
        self.log.debug("Le match a commencé!")
        with self.mutex:
            self.date_debut = time()
            self.match_demarre = True

    def run(self):
        """
        Le thread timer, qui supprime les obstacles périssables et arrête le robot à la fin du match.
        """
        self.log.debug("Lancement du thread timer")
        self.initialisation()
        while time() - self.get_date_debut() < self.config["temps_match"]:
            if AbstractThread.stop_threads:
                self.log.debug("Stoppage du thread timer")
                return None
            sleep(.5)
            
        with self.mutex:
            self.fin_match = True
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.robot.deplacements.arret_final()
        self.log.debug("Fin du thread timer")
        
    def get_date_debut(self):
        """
        Getter de la variable date_debut
        """
        with self.mutex:
            return self.date_debut

    def get_fin_match(self):
        """
        Getter de la variable fin_match
        """
        with self.mutex:
            return self.fin_match