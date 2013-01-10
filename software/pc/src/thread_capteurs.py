from outils_maths.point import Point
from math import cos
from math import sin

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
    log.debug("lancement du thread de capteurs")

    while not timer.fin_match:
        distance=capteurs.mesurer(robot.marche_arriere)
        if distance>=0:
            x=robot.x+distance*cos(robot.orientation)
            y=robot.y+distance*sin(robot.orientation)
            if not x<(-config["table_x"]/2) or y<0 or x>config["table_x"]/2 or y>config["table_y"]:
                table.cree_obstaclesCapteur(Point(x,y))
        sleep(0.1)

