import threading
from mutex import Mutex
from outils_maths.point import Point
from outils_maths.vitesse import Vitesse
from math import cos,sin,pi
from time import sleep,time
import socket

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

        while not timer.get_fin_match():
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread capteurs")
                return None
            
            distance = capteurs.mesurer(robot.marche_arriere)
            if distance >= 0:
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
    def __init__(self, log, config, robot, table, capteurs):
        AbstractThread.__init__(self, None)
        self.log = log
        self.config = config
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
        self.match_demarre = False
        self.fin_match = False
        self.mutex = Mutex()

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
            sleep(.5)
        with self.mutex:
            self.fin_match = True
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.robot.gonflage_ballon()
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

   
class ThreadLaser(AbstractThread):
    
    def __init__(self, container):
        AbstractThread.__init__(self, container)
        
    def run(self):
        """
        Cette fonction sera lancée dans un thread parallèle à la stratégie.
        Les différentes balises sont intérrogées régulièrement, les résultats sont filtrés puis passés au service de table
        """
        
        # importation des services nécessaires
        log = self.container.get_service("log")
        config = self.container.get_service("config")
        laser = self.container.get_service("laser")
        filtrage = self.container.get_service("filtrage")
        table = self.container.get_service("table")
        timer = self.container.get_service("threads.timer")

        log.debug("Lancement du thread des lasers")

        # Attente du démarrage du match et qu'au moins une balise réponde
        while not timer.match_demarre or laser.verifier_balises_connectes() == 0:
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread laser")
                return None
            sleep(0.1)
            
        # Allumage des lasers
        laser.allumer()
            
        # Liste des balises non prises en compte
        for balise in laser.balises_ignorees():
            log.warning("balise n°" + str(balise["id"]) + " ignorée pendant le match, pas de réponses aux ping")

        # Liste des balises prises en compte
        balises = laser.balises_actives()
        
        while not timer.get_fin_match():
            start = time()
            
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread laser")
                return None
            
            for balise in balises:
                
                # Récupération de la position brute
                p_bruit = laser.position_balise(balise["id"])
                
                # Aucune réponse valable
                if p_bruit is None:
                    continue
                    
                # Mise à jour du modèle de filtrage
                filtrage.update(p_bruit.x, p_bruit.y)
                
                # Récupération des valeurs filtrées
                p_filtre = filtrage.position()
                vitesse = filtrage.vitesse()
                
                # Mise à jour de la table
                table.deplacer_robot_adverse(0, p_filtre, vitesse)

                # Affichage des points sur le simulateur
                if config["cartes_simulation"] != ['']:
                    simulateur = self.container.get_service("simulateur")
                    if config["lasers_afficher_valeurs_brutes"]:
                        simulateur.drawPoint(p_bruit.x, p_bruit.y, "gris")
                    if config["lasers_afficher_valeurs_filtre"]:
                        simulateur.drawPoint(p_filtre.x, p_filtre.y, "blue")
            
            sleep(1./config["lasers_frequence"])
            
            # Mise à jour de l'intervalle de temps pour le filtrage
            end = time()
            filtrage.update_dt(end-start)
            
        log.debug("Fin du thread des lasers")
        
        
class ThreadCouleurBougies(AbstractThread):
    
    def __init__(self, container):
        super().__init__(container)
        
    def run(self):
        """
        Cette fonction sera lancée dans un thread parallèle à la stratégie.
        Une socket vers le téléphone est ouverte pour récupérer les couleurs des bougies
        """
        # importation des services nécessaires
        log = self.container.get_service("log")
        config = self.container.get_service("config")
        table = self.container.get_service("table")
        timer = self.container.get_service("threads.timer")
        scripts = self.container.get_service("scripts")

        log.debug("Lancement du thread de détection des couleurs des bougies (mais attente du jumper)")

        # Attente du démarrage du match
        while not timer.match_demarre:
            if AbstractThread.stop_threads:
                log.debug("Stoppage du thread de détection des couleurs des bougies")
                return None
            sleep(0.1)
            
        # Ouverture de la socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.settimeout(config["timeout_android"])
            client_socket.connect((config["ip_android"], 8080))
            client_socket.send(bytes(config["couleur"][0]+"\n", 'UTF-8'))
            rcv = str(client_socket.recv(11),"utf-8").replace("\n","")
            table.definir_couleurs_bougies(rcv)
        except:
            # Si on n'a pas d'information de l'appli android, le mieux est de faire toutes les bougies (ce qui permet de gagner le plus de points possible). Pour cela, on contourne la complétion antisymétrique effectuée dans définir_couleur_bougies
            couleur_bougies = table.COULEUR_BOUGIE_BLEU if config["couleur"]=="bleu" else table.COULEUR_BOUGIE_ROUGE
            for i in range (20):
                table.bougies[i]["couleur"] = couleur_bougies
            #le script tiendra compte de ce comportement dans le décompte des points
            if "ScriptBougies" in scripts:
                scripts["ScriptBougies"].en_aveugle = True
        finally:
            client_socket.close()
           
        log.debug("Fin du thread de détection des couleurs des bougies")
        
