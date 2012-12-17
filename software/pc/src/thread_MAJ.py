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
    
    log.debug("lancement du thread de mise à jour")
    
    #le reste du code attend une première mise à jour des coordonnées
    robot_pret = False
    while not robot_pret:
        try:
            robot.update_x_y_orientation()
            robot_pret = True
        except Exception as e:
            print(e)
        sleep(0.1)
    robot.pret = True
    
    while 42:
    
        #mise à jour des coordonnées dans robot
        try:
            robot.update_x_y_orientation()
        except Exception as e:
            print(e)
        
        sleep(0.1)