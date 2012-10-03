
class Script:

    def __init__(self,robot,config):
        
        #instances des dépendances
        self.robot = robot
        self.config = config
        
        
        self.robot.deplacements.parle()

        
class Script_bougies(Script):
    
    def __init__(self,robot,config):
        Script.__init__(self,robot,config)
        
        #dictionnaire définissant les bougies actives ou non
        self.bougies = {"bougie1" : False, "bougie2" : True, "bougie3" : True, "bougie4" : True}