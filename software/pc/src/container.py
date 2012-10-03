#importation de la configuration
from src.read_ini import Config,Constantes
import os

#module d'injection de dépendances
from src.assemblage import assembler

#modules
from src.robot import Robot
from src.deplacements import Deplacements_simu, Deplacements_serie
from src.scripts import Script, ScriptBougies
from src.log import Log

class Container:
    def __init__(self):
        self.assembler = assembler()
        
        #retrouve le chemin de la racine "software/pc"
        directory = os.path.dirname(os.path.abspath(__file__))
        racine = "software/pc"
        chemin = directory[:directory.index(racine)]+racine
        
        #enregistrement du service de configuration
        def make_conf():
            conf = Config()
            conf.set_chemin(chemin+"/config")
            return conf
        self.assembler.register(Config,factory=make_conf)
        
        #utilisation du service de configuration pour la suite
        self.config = self.get_service(Config)
        
        #enregistrement du service des logs
        def make_log(config):
            log = Log(self.config)
            log.set_chemin(chemin)
            return log
        self.assembler.register(Log, requires = [Config], factory=make_log)
        
        #enregistrement du service des déplacements
        if (self.config["mode_simulateur"]):
            Deplacements = Deplacements_simu
        else:
            Deplacements = Deplacements_serie
        self.assembler.register(Deplacements, requires=[Config,Log])
        
        #enregistrement du service robot
        self.assembler.register(Robot, requires=[Deplacements,Config,Log])
        
    def get_service(self,type):
        return self.assembler.provide(type)
        