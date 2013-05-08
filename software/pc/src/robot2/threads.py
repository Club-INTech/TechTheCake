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
        
class ThreadCapteurs(AbstractThread):
    
    def __init__(self, container):
        AbstractThread.__init__(self, container)
        
    def run(self):
        """
        Cette fonction sera lancée dans un thread parallèle à la stratégie.
        Celle-ci récupère la distance des capteurs et le transforme en (x,y) donnés au service table
        """
        
        log = self.container.get_service("log")
        config = self.container.get_service("config")
        robot = self.container.get_service("robot")
        capteurs = self.container.get_service("capteurs")
        table = self.container.get_service("table")
        timer = self.container.get_service("threads.timer")

        log.debug("Lancement du thread de capteurs")

        # Attente du début de match
        while not timer.match_demarre:
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread capteurs")
                return None
            sleep(0.1)

        # On attendra un peu avant d'enregistrer un nouvel obstacle. Valeur à tester expérimentalement.
        tempo = config["capteurs_temporisation_obstacles"]
        
        # On retire self.tempo afin de pouvoir directement ajouter un nouvel objet dès le début du match.
        # Attention: le match doit être démarré pour utiliser date_debut         
        dernier_ajout = 0

        log.debug("Activation des capteurs")
        while not timer.get_fin_match():
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread capteurs")
                return None
            distance = capteurs.mesurer(robot.marche_arriere)
            if distance >= 0 and distance <= 1000:
                #distance : entre le capteur situé à l'extrémité du robot et la facade du robot adverse
                distance_inter_robots = distance + config["rayon_robot_adverse"] + config["largeur_robot"]/2
                if robot.marche_arriere:
                    x = robot.x - distance_inter_robots * cos(robot.orientation)
                    y = robot.y - distance_inter_robots * sin(robot.orientation)
                else:
                    x = robot.x + distance_inter_robots * cos(robot.orientation)
                    y = robot.y + distance_inter_robots * sin(robot.orientation)

                # Vérifie que l'obstacle n'a pas déjà été ajouté récemment
                if time() - dernier_ajout > tempo:
                    # Vérifie si l'obstacle est sur la table 
                    if x > (-config["table_x"]/2) and y > 0 and x < config["table_x"]/2 and y < config["table_y"]:
                        # Vérifie que l'obstacle perçu n'est pas le gateau
                        if not ((x-0)**2 + (y-2000)**2) < 550**2:
                            table.creer_obstacle(Point(x,y))
                            dernier_ajout = time()   
                    
            sleep(1./config["capteurs_frequence"])
            
        log.debug("Fin du thread de capteurs")

class ThreadTimer(AbstractThread):
    """
    Classe de gestion du temps et d'appels réguliers.
    Deux variables globales sont très utilisées: timer.fin_match et timer.match_demarre. 
    Supprime les obstacles périssables du service de table.
    """
    def __init__(self, log, config, robot, table, capteurs, son):
        AbstractThread.__init__(self, None)
        self.log = log
        self.config = config
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
        self.son = son
        self.match_demarre = False
        self.fin_match = False
        self.mutex = Mutex()
        self.compte_rebours = True

    def initialisation(self):
        """
        Boucle qui attend le début du match et qui modifie alors la variable timer.match_demarre
        """
        while not self.capteurs.demarrage_match() and not self.match_demarre:
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
            self.table.supprimer_obstacles_perimes()

            #son aléatoire            
            if randint(0,200) == 0:
                self.son.jouer("random")

            #son compte-à-rebours
            if time() - self.get_date_debut() > self.config["temps_match"] - 4 and self.compte_rebours:
                self.son.jouer("compte_rebours", force=True)
                self.compte_rebours = False

            sleep(.5)
        with self.mutex:
            self.fin_match = True
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.robot.gonflage_ballon()
        self.robot.deplacements.arret_final()
        self.son.jouer("generique", force=True, enBoucle=True)
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