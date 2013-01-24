from time import time
from time import sleep
from mutex import Mutex

class Timer():
    """
    Classe de gestion du temps et d'appels réguliers.
    Deux variables globales sont très utilisées: timer.fin_match et timer.match_demarre. 
    Supprime les obstacles périssables du service de table.
    """
    def __init__(self, log, config, robot, table, capteurs):
        self.log = log
        self.config = config
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
        self.match_demarre = False
        self.fin_match = False
        self.mutex=Mutex()

    def initialisation(self):
        """
        Boucle qui attend le début du match et qui modifie alors la variable timer.match_demarre
        """
        while not self.capteurs.demarrage_match():
            sleep(.5)
        self.log.debug("Le match a commencé!")
        with self.mutex:
            self.match_demarre = True
            self.date_debut = time()

    def _suppression_obstacles(self):
        dates_naissance_obstacles=self.table.get_obstaclesCapteur()
        #print(dates_naissance_obstacles)
        i=0
        while i<len(dates_naissance_obstacles) and (dates_naissance_obstacles[i].naissance+self.config["duree_peremption_obstacles"])>time():   #une recherche dichotomique serait peut-être plus efficace, mais comme l'indice recherché est probablement petit... ça se discute.
            i=i+1
        if i<len(dates_naissance_obstacles):
            self.table.maj_obstaclesCapteur(i)

    def thread_timer(self):
        """
        Le thread timer, qui supprime les obstacles périssables et arrête le robot à la fin du match.
        """
        self.log.debug("Lancement du thread timer")
        self.initialisation()
        while (time()-self.get_date_debut())<self.config["temps_match"]:
            self._suppression_obstacles()
            sleep(.5)
        with self.mutex:
            self.fin_match = True
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.robot.gonflage_ballon()

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

    


#TODO
#Méthodes à mettre en place:
#
#demarrage_match() dans le service capteurs qui renvoie un booléen
#timestamp_obstacles() dans le service table qui renvoie une liste contenant les timestamps de tous les obstacles en disposant. Attention, cette liste est supposée triée (car on la remplit par ordre d'arrivée, et donc par ordre de départ)
#supprimer_obstacles(entier i) dans le service table qui supprime les obstacles temporaires à partir de l'indice i (compris)
#gonflage_ballon() dans le service robot qui lance le gonflage du ballon

