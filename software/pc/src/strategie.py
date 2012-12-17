from time import sleep
from scripts import *

class Strategie:
    def __init__(self, robot, robotChrono,hookGenerator, rechercheChemin, config, log):
        
        #services importés
        self.robot = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.config = config
        self.log = log
        
        self.scripts = {"bougies":ScriptBougies, "hooks":ScriptTestHooks, "testCadeaux":ScriptTestCadeaux}
    
        for script,classe in self.scripts.items():
            self.scripts[script] = classe()
            self.scripts[script].set_dependencies(self.robot, self.robotChrono, self.hookGenerator, self.log, self.config)
        
    def boucle_pipeau(self):
        while 1 :
            self.log.debug(str(self.robot.get_x())+", "+str(self.robot.get_y())+", "+str(self.robot.get_orientation()))
            sleep(0.1)
            