from time import sleep
from scripts import *

class Strategie:
    def __init__(self, container):
        
        #services importés
        self.config = container.get_service("config")
        self.log = container.get_service("log")
        self.robot = container.get_service("robot")
        self.robotChrono = container.get_service("robotChrono")
        
        self.scripts = {"bougies":ScriptBougies, "pipeau":ScriptPipeau}
    
        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.log, self.config)
        
    def boucle_pipeau(self):
        while 1 :
            self.log.debug(str(self.robot.get_x())+", "+str(self.robot.get_y())+", "+str(self.robot.get_orientation()))
            sleep(0.1)
            