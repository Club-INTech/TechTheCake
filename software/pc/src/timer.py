from time import time
from time import sleep

class Timer():

    def __init__(self, log, config, robot, table, capteurs):
        self.log = log
        self.config = config
        self.robot = robot
        self.table = table
        self.capteurs = capteurs
        self.match_demarre = False
        self.fin_match = False

    def initialisation(self):
        if not self.config["mode_simulateur"]:  #si on est en mode simulateur, on commence de suite
            while not self.capteurs.demarrage_match():
                sleep(.5)
        self.log.debug("Le match a commencé!")
        self.match_demarre = True
        self.date_debut = time()

    def suppression_obstacles(self):
        dates_naissance_obstacles=self.table.get_obstaclesCapteur()
        #print(dates_naissance_obstacles)
        i=0
        while i<len(dates_naissance_obstacles) and (dates_naissance_obstacles[i]+self.config["duree_peremption_obstacles"])>time():   #une recherche dichotomique serait peut-être plus efficace, mais comme l'indice recherché est probablement petit... ça se discute.
            i=i+1
        if i<len(dates_naissance_obstacles):
            self.table.maj_obstaclesCapteur(i)

    def thread_timer(self):
        self.log.debug("Lancement du thread timer")
        self.initialisation()
        while (time()-self.date_debut)<self.config["temps_match"]:
            self.suppression_obstacles()
            sleep(.5)
        self.fin_match = True
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

