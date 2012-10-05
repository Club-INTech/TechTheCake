from time import sleep
from robot import Robot
from serie import Serie
from log import Log

def fonction_MAJ(container):
    log = container.get_service("log")
    robot = container.get_service("robot")
    
    log.debug("lancement du thread de mise à jour")
    while 42:
        
        log.debug("thread")
        #infos_blocage = robot.deplacements.get_infos_stoppage()
        #robot.gestion_blocage(*infos_blocage)
        
        #infos_enMouvement = robot.deplacements.get_infos_enMouvement()
        #robot.update_enMouvement(*infos_enMouvement)
        
        infos_x_y_orientation = robot.deplacements.get_infos_x_y_orientation()
        robot.update_x_y_orientation(*infos_x_y_orientation)
        
        sleep(0.5)