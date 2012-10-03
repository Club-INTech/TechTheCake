
class Script:

    def __init__(self,robot,config,log):
        
        #instances des dépendances
        self.robot = robot
        self.config = config
        self.log = log
        
        
        self.robot.deplacements.parle()

        
class ScriptBougies(Script):
    
    def __init__(self,robot,config,log):
        Script.__init__(self,robot,config,log)
        
        #dictionnaire définissant les bougies actives ou non
        self.bougies = {"bougie1" : False, "bougie2" : True, "bougie3" : True, "bougie4" : True}
        