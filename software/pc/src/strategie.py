from time import sleep
from scripts import *

class Strategie:
    def __init__(self, container):
        
        #services importés
        self.config = container.get_service("config")
        self.log = container.get_service("log")
        self.robot = container.get_service("robot")
    
        #instanciation des classes de script, et de leurs dépendances
        for script in ["ScriptBougies"]:
            exec("self.instance"+script+" = "+script+"()")
            exec("self.instance"+script+".set_dependencies(self.robot, self.log, self.config)")
        
    def boucle_pipeau(self):
        while 1 :
            self.log.warning(str(self.robot.get_orientation()))
            sleep(1)