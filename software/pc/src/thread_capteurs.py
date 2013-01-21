from outils_maths.point import Point
from math import cos,sin
from time import sleep
from time import time

def fonction_capteurs(container):
    """
    Cette fonction sera lancée dans un thread parallèle à la stratégie.
    Celle-ci récupère la distance des capteurs et le transforme en (x,y) donnés au service table
    """
    
    #importation des services nécessaires
    log = container.get_service("log")
    config = container.get_service("config")
    robot = container.get_service("robot")
    capteurs = container.get_service("capteurs")
    table = container.get_service("table")
    timer = container.get_service("timer")

    log.debug("Lancement du thread de capteurs")

    while not timer.match_demarre:
        sleep(0.1)

    tempo=config["temporisation_obstacles"]         #on attendra 500 ms avant d'enregistrer un nouvel obstacle. Valeur à tester expérimentalement.
    dernier_ajout=timer.date_debut-tempo            #on retire self.tempo afin de pouvoir directement ajouter un nouvel objet dès le début du match. Attention: le match doit être démarré pour utiliser date_debut

    while not timer.get_fin_match():
        distance=capteurs.mesurer(robot.marche_arriere)
        if distance>=0:                             #cette condition ne sert que dans le simulateur (les conventions pour les objets à l'infini diffèrent)
            x=robot.x+distance*cos(robot.orientation)
            y=robot.y+distance*sin(robot.orientation)
            if x>(-config["table_x"]/2) and y>0 and x<config["table_x"]/2 and y<config["table_y"] and time()-dernier_ajout>tempo:
                table.cree_obstaclesCapteur(Point(x,y))
                dernier_ajout=time()
        sleep(0.1)
    log.debug("Arrêt du thread de capteurs")

