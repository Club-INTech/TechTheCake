from time import sleep
from math import pi
from outils_maths.point import Point

class Script:
    """
    classe mère des scripts
    se charge des dépendances
    """
    def set_dependencies(self, robot, robotChrono, hookGenerator, log, config):
        
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
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
        self.robot.gestion_avancer(300)
        self.robot.gestion_tourner(pi/2)
        self.robot.gestion_avancer(500)
        
class ScriptTestHooks(Script):
    
    def execute(self):
            
        def aFaire(texte):
            print("appel du callback : "+texte)
            
        hooks = []
        hooks.append(self.hookGenerator.get_hook("position", Point(910,300), aFaire, "lapin", unique = False))
        hooks.append(self.hookGenerator.get_hook("orientation", pi, aFaire, "chèvre"))
        
        self.robot.gestion_avancer(300,hooks)
        self.robot.gestion_tourner(pi/2,hooks)
        self.robot.gestion_avancer(500,hooks)