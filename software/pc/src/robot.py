from time import time

class Robot:
    #constantes de classe pour définir l'état de l'acquittement
    moving = 0
    arrived = 1
    stopped = 2
    
    def __init__(self,deplacements,config,log):
        
        #instances des dépendances
        self.deplacements = deplacements
        self.config = config
        self.log = log
        
        #attributs "physiques"
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.debut_jeu = time()
        self.acquittement = self.arrived