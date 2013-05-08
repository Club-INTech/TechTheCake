from time import sleep,time
import robot
from outils_maths.point import Point
import recherche_de_chemin.rechercheChemin as libRechercheChemin

class Comportement:
    """
    Classe gérant l'intelligence artificielle du robot secondaire. 
    """
    def __init__(self, rechercheChemin, timer, config, log, robot):

        self.rechercheChemin = rechercheChemin
        self.timer = timer
        self.config = config
        self.log = log
        self.robot = robot

    def boucle_comportement(self):
        """
        Boucle qui gère le comportement. 
        """
        while not self.timer.match_demarre:
            sleep(.5)
            
        self.log.debug("Début du comportement.")
        while not self.timer.get_fin_match():
            pass