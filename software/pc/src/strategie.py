from time import sleep
from scripts import *

class Strategie:
    def __init__(self, robot, robotChrono, hookGenerator, rechercheChemin, table, timer, config, log):

        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log

        self.scripts = {"pipeau1":ScriptPipeauStrategie1, "pipeau2":ScriptPipeauStrategie2, "pipeau3":ScriptPipeauStrategie3,"bougies":ScriptBougies, "hooks":ScriptTestHooks, "recalcul":ScriptTestRecalcul}
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]
        self.points={"cadeau":0, "verres": 0, "gateau":0, "deposer_verre":0, "pipeau1":6, "pipeau2": 12, "pipeau3":8}

        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.rechercheChemin, self.config, self.log)
        
    def boucle_strategie(self):
        self.log.debug("Stratégie lancée.")
        while not self.timer.fin_match:
            note={"cadeau":0, "verreNous":0, "verreEnnemi": 0, "gateau":0, "deposer_verres":0, "pipeau1":0, "pipeau2":0, "pipeau3":0}

        #        for script in self.points: #retiré pour la durée des tests (tant que les vrais scripts ne sont pas dispo...)
        #            self.points[script]=0
            self.points["deposer_verre"]=6#(nb verre)
            for element in self.table.bougies:
                if not element["traitee"]:
                    self.points["gateau"]+=2 #chaque bougie rapporte 4 points, mais la moitié des bougies sont à l'ennemi...
            for element in self.table.verres:
                if element["present"]:
                    self.points["verres"]+=6
            for element in self.table.cadeaux:
                if not element["ouvert"]:
                    self.points["cadeau"]+=4

            for script in self.scripts:
                dureeScript=self.scripts[script].calcule()
                distanceE=self.distance_ennemi()
                note[script]=10000000*self.points[script]/(dureeScript*dureeScript*dureeScript*distanceE*distanceE) #cette formule est aussi valable pour deposer_verres
                self.log.debug("Note du script "+script+": "+str(note[script]))

            noteInverse = dict(map(lambda item: (item[1],item[0]),note.items()))
            scriptAFaire=noteInverse[max(noteInverse.keys())]   #ce script a reçu la meilleure note

            self.log.debug("La stratégie a décidé d'exécuter le script: "+scriptAFaire)
            if not self.timer.fin_match:
                self.scripts[scriptAFaire].agit()

            sleep(0.1)
        log.debug("Arrêt de la stratégie.")

    def distance_ennemi(self):

#                self.table.RobotAdverseBalise
#                self.table.
        return 42
    
#TODO
#dans robot, il faut le nombre de verres dans chaque ascenseur. dans config, le nombre de verres max?
