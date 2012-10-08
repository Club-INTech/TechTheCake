from time import sleep
from scripts import *

class Strategie:
    def __init__(self, container):
        
        #services importés
        self.config = container.get_service("config")
        self.log = container.get_service("log")
        self.robot = container.get_service("robot")
        
        self.scripts = {"bougies":ScriptBougies}
    
        #for script,classe in self.scripts.items():
            #self.scripts[script] = classe()
            #self.scripts[script].set_dependencies(self.robot, self.log, self.config)
        
    def boucle_pipeau(self):
        while 1 :
            self.log.debug(str(self.robot.get_x())+", "+str(self.robot.get_y())+", "+str(self.robot.get_orientation()))
            sleep(0.1)
            
    def controleur(self):
        
        #self.robot.tourner(0.1)
        #self.robot.avancer(600)
        #self.robot.tourner(-1.57)
        #self.robot.avancer(1000)
        #sleep(3)
        #self.robot.avancer(500)
        
        self.robot.recaler()
        