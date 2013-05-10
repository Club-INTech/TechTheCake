from time import sleep

class Actionneurs :

    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
    def actionneur_balai(self, position) :
        if position == "ouvert":
            self.serie.communiquer("capteurs_actionneurs",["gauche",100],0)
            self.serie.communiquer("capteurs_actionneurs",["droit",100],0)
        else:
            self.serie.communiquer("capteurs_actionneurs",["gauche",0],0)
            self.serie.communiquer("capteurs_actionneurs",["droit",0],0)

    def actionneur_balai(self, position) :
        if position == "ouvert":
            self.serie.communiquer("capteurs_actionneurs",["casse",100],0)
        else:
            self.serie.communiquer("capteurs_actionneurs",["casse",0],0)
            