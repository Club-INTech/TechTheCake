
class Script:

    def __init__(self):
        
        #instances des dépendances
        self.robot = robot
        self.config = config
        self.log = log
        
        
        self.robot.deplacements.parle()
        
        def set_log(self,log):
            self.log = log

        
class ScriptBougies(Script):
    
    def __init__(self):
        #dictionnaire définissant les bougies actives ou non
        self.bougies = {"bougie1" : False, "bougie2" : True, "bougie3" : True, "bougie4" : True}
        
        
        
        

#sb = ScriptBougies()
#sb.set_log()