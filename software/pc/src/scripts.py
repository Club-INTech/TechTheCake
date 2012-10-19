from time import sleep
class Script:
    """
    classe mère des scripts
    se charge des dépendances
    """
    def set_dependencies(self, robot, robotChrono, log, config):
        
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.log = log
        self.config = config

    def agit(self):
        self.robot = self.robotVrai
        self.execute()
        
    def calcule(self):
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.execute()
        return self.robot.get_compteur()
        
    
        
class ScriptBougies(Script):
    """
    exemple de classe de script pour les bougies
    hérite de la classe mère Script
    """
    
    def __init__(self):
        #dictionnaire définissant les bougies actives ou non
        self.bougies = {"bougie1" : False, "bougie2" : True, "bougie3" : True, "bougie4" : True}
        
    def execute(self):
        pass
    
    
class ScriptPipeau(Script):
    
    def execute(self):
        self.robot.gestion_tourner(0.1)
        self.robot.gestion_avancer(600)
        self.robot.gestion_tourner(-1.57)
        self.robot.gestion_avancer(1000)
        self.robot.gestion_avancer(-500)
        
        #self.robot.recaler()