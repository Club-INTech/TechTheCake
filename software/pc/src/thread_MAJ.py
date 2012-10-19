from time import sleep
from robot import Robot
from serie import Serie
from log import Log

def fonction_MAJ(container):
    """
    cette fonction sera lancée dans un thread parallèle à la stratégie
    il met à jour les attributs "physiques" du robot (coordonnées, acquittement...)
    et stoppe automatiquement le robot en cas de blocage
    """
    
    #importation des services nécessaires
    log = container.get_service("log")
    robot = container.get_service("robot")
    #table = container.get_service("table")
    #capteurs = container.get_service("capteurs")
    
    log.debug("lancement du thread de mise à jour")
    while 42:
    
        #mise à jour des coordonnées dans robot
        robot.update_x_y_orientation()
        
        sleep(0.2)
                    
