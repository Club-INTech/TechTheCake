from time import sleep

class Actionneurs :

    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
    def actionneur_balai(self, position) :
        if position == "ouvert":
            self.serie.communiquer("capteurs_actionneurs",["balai",100],0)
        elif position == "ferme":
            self.serie.communiquer("capteurs_actionneurs",["balai",0],0)
