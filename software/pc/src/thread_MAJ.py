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
        infos_xyo = robot.deplacements.get_infos_x_y_orientation()
        
        robot.update_x_y_orientation(*infos_xyo)
        
        #récupération des informations bas niveau nécessaires pour gestion_blocage et update_enMouvement
        infos_stoppage_enMouvement = robot.deplacements.get_infos_stoppage_enMouvement()
        
        #mise à jour de l'attribut enMouvement du robot
        robot.enMouvement = robot.deplacements.update_enMouvement(**infos_stoppage_enMouvement)
        
        #si un blocage est detecté, l'inscrire dans un attribut du robot
        if robot.deplacements.gestion_blocage(**infos_stoppage_enMouvement):
            if not robot.blocage :
                robot.deplacements.stopper()
                robot.blocage = True
                robot.enMouvement = False
        
        sleep(0.01)
                    