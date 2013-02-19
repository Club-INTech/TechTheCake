from outils_maths.point import Point
from math import cos,sin
from time import sleep
from time import time

def fonction_capteurs(container):
    """
    Cette fonction sera lancée dans un thread parallèle à la stratégie.
    Celle-ci récupère la distance des capteurs et le transforme en (x,y) donnés au service table
    """
    
    log = container.get_service("log")
    config = container.get_service("config")
    robot = container.get_service("robot")
    capteurs = container.get_service("capteurs")
    table = container.get_service("table")
    timer = container.get_service("timer")

    log.debug("Lancement du thread de capteurs")

    # Attente du début de match
    while not timer.match_demarre:
        sleep(0.1)

    # On attendra un peu avant d'enregistrer un nouvel obstacle. Valeur à tester expérimentalement.
    tempo = config["capteurs_temporisation_obstacles"]
    
    # On retire self.tempo afin de pouvoir directement ajouter un nouvel objet dès le début du match.
    # Attention: le match doit être démarré pour utiliser date_debut         
    dernier_ajout = timer.date_debut - tempo

    while not timer.get_fin_match():
        distance = capteurs.mesurer(robot.marche_arriere)
        
        if distance >= 0:                       
            x = robot.x + (distance + config["rayon_robot_adverse"]/2) * cos(robot.orientation)
            y = robot.y + (distance + config["rayon_robot_adverse"]/2) * sin(robot.orientation)
            
            # Vérifie si l'obstacle est sur la table et qu'il n'a pas déjà été ajouté récemment
            if x > (-config["table_x"]/2) and y > 0 and x < config["table_x"]/2 and y < config["table_y"] and time() - dernier_ajout > tempo:
                table.creer_obstacle(Point(x,y))
                dernier_ajout = time()   
                
        sleep(1./config["capteurs_frequence"])
        
    log.debug("Arrêt du thread de capteurs")

