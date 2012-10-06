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
    while 42:
        
        #mise à jour des coordonnées dans robot
        infos_xyo = robot.deplacements.get_infos_x_y_orientation()
        robot.update_x_y_orientation(*infos_xyo)
        
        #mise à jour de l'état du robot (en mouvement, stoppé, à la consigne), et gestion du blocage automatique
        infos_stoppage_enMouvement = robot.deplacements.get_infos_stoppage_enMouvement()
        robot.update_enMouvement(**infos_stoppage_enMouvement)
        robot.gestion_blocage(**infos_stoppage_enMouvement)