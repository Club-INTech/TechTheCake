from time import sleep

def fonction_MAJ(container):
    """
    Cette fonction sera lancée dans un thread parallèle à la stratégie.
    Celui-ci met à jour les attributs "physiques" du robot (coordonnées x, y et orientation).
    Au démarrage, il bloque les autres threads, afin d'attendre une première mise à jour des coordonnées.
    """
    
    #importation des services nécessaires
    log = container.get_service("log")
    robot = container.get_service("robot")
    timer = container.get_service("timer")
    
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
    
    while not timer.get_fin_match():
    
        #mise à jour des coordonnées dans robot
        try:
            robot.update_x_y_orientation()
        except Exception as e:
            print(e)
        
        sleep(0.1)
    log.debug("Arrêt du thread de mise à jour")

