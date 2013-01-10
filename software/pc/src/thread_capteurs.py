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
    
    log.debug("lancement du thread de capteurs")

    while 1:
        self.distance=capteurs.mesurer(robot.marche_arriere)
        if self.distance>=0:
            self.x=robot.x+distance*cos(robot.orientation)
            self.y=robot.y+distance*sin(robot.orientation)
            if x<5 or y<5 or x>config.["table_x"]-5 or y>config.["table_y"]-5:
                table.cree_obstaclesCapteur('(' + str(self.x) + ',' + str(self.y) + ')')
        sleep(0.1)

