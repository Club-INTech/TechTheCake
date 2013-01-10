from time import time
from time import sleep

class Timer():

    def __init__(self, robot, table, capteurs):
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
#       self.actionneurs = actionneurs
        self.match_demarre = False

    def initialisation()
        while not self.capteurs.demarrage_match():
        match_demarre = True
        self.date_debut = time.time()

    def suppression_obstacles()
        timestamp_obstacles=self.table.get_obstaclesCapteur()
        i=0
        while i<timestamp_obstacles.length and timestamp_obstacles[i]>(time.time()-date_debut):   #une recherche dichotomique serait peut-être plus efficace, mais comme l'indice recherché est probablement petit... ça se discute.
            i=i+1
        if i>=0:
            self.table.maj_obstaclesCapteur(i)

    def thread_timer()
        self.initialisation()
        while (time.time()-date_debut)<self.config.["temps_match"]:
            self.suppression_obstacles()
            sleep(.5)
#        self.?.stop() #on arrête la stratégie avant le robot, sinon le robot risque de repartir avant qu'on arrête la stratégie
#pour l'instant, la stratégie s'arrête toute seule
        self.capteurs.stop()
        self.robot.stopper()
        sleep(.500) #afin d'être sûr que le robot a eu le temps de s'arrêter
        self.robot.deplacements.desactiver_asservissement_translation()
        self.robot.deplacements.desactiver_asservissement_rotation()
        self.robot.gonflage_ballon()


#TODO
#Méthodes à mettre en place:
#
#demarrage_match() dans le service capteurs qui renvoie un booléen
#timestamp_obstacles() dans le service table qui renvoie une liste contenant les timestamps de tous les obstacles en disposant. Attention, cette liste est supposée triée (car on la remplit par ordre d'arrivée, et donc par ordre de départ)
#supprimer_obstacles(entier i) dans le service table qui supprime les obstacles temporaires à partir de l'indice i (compris)
#gonflage_ballon() dans le service robot qui lance le gonflage du ballon

