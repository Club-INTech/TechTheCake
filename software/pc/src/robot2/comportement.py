import time
import robot
from outils_maths.point import Point

class Comportement:
    """
    Classe gérant l'intelligence artificielle du robot secondaire. 
    """
    def __init__(self, timer, robot, com2principal, config, log):

        self.timer = timer
        self.robot = robot
        self.com2principal = com2principal
        self.config = config
        self.log = log

    def boucle_comportement(self):
        """
        Boucle qui gère le comportement. 
        """
        while not self.timer.match_demarre:
            time.sleep(.5)
            
        self.log.debug("Début du comportement.")

        while not self.timer.get_fin_match():
            # enregistrement des cases de départ de l'adverse données par la balise
            if not hasattr(self, 'cases_adverse') and time.time() - self.timer.get_date_debut() > 3:
                nb_cases = self.com2principal.nb_cases_depart_adverse()
                self.cases_adverse = self.com2principal.cases_depart_adverse(nb_cases)
                
            # élection d'une action paramétrée
            action, version = self.elit_action()
            
            # effectue l'action
            action(version)
            
    def elit_action(self):
        
        zone_a_eviter = self.com2principal.zone_action_robot1()
        
        
    def balayer_verres(self, zone_trajet):
        """
        Balaye les verres du coté adverse, en passant par la zone passée en paramètre. 
        """
        self.robot.va_au_point(Point(200, 1000))
    