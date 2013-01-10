class Timer():

    def __init__(self, robot, table, capteurs, actionneurs):
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
        self.actionneurs = actionneurs
        self.match_demarre = False

    def initialisation()
        while not self.capteurs.demarrage_match():
        match_demarre = True
        self.date_debut = time.time()

    def suppression_obstacles()
        timestamp_obstacles=self.table.timestamp_obstacles()
        i=-1
        while timestamp_obstacles[i+1]<(time.time()-date_debut):   #une recherche dichotomique serait peut-être plus efficace, mais comme l'indice recherché est probablement petit... ça se discute.
            i=i+1
        self.table.supprimer_obstacles(i)

    def thread_timer()
        self.initialisation()
        while (time.time()-date_debut)<self.config.["temps_match"]:
            self.suppression_obstacles()
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.strategie.stop()
        self.robot.gonflage_ballon()


#TODO
#Méthodes à mettre en place:
#
#demarrage_match() dans le service capteurs qui renvoie un booléen
#timestamp_obstacles() dans le service table qui renvoie une liste contenant les timestamps de tous les obstacles en disposant. Attention, cette liste est supposée triée (car on la remplit par ordre d'arrivée, et donc de départ)
#supprimer_obstacles(entier i) dans le service table qui supprime les obstacles temporaires jusqu'à l'indice i (compris). Attention, si i=-1, il ne faut rien supprimer!
#gonflage_ballon() dans le service robot qui lance le gonflage du ballon
