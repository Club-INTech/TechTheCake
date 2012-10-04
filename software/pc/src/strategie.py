from time import sleep
from scripts import *

class Strategie:
    def __init__(self, robot, log, config):
        #service de logs
        self.log = log
        #instanciation des classes de script, et de leurs dépendances
        for script in ["ScriptBougies"]:
            exec("self.instance"+script+" = "+script+"()")
            exec("self.instance"+script+".set_dependencies(robot, log, config)")
        
    def boucle_pipeau(self):
        while 1 :
            self.log.debug("_________")
            sleep(2)