import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine

#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#module d'injection de dépendances
from assemblage import assembler

#modules
from read_ini import Config
from robot import *
from deplacements import Deplacements_simu, DeplacementsSerie
from serie import Serie
from scripts import Script, ScriptBougies
from log import Log

class Container:
    def __init__(self):
        self.assembler = assembler()
        
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
        
        #enregistrement du service Serie
        self.assembler.register(Serie)
        
        #enregistrement du service des déplacements
        if (self.config["mode_simulateur"]):
            Deplacements = Deplacements_simu
            self.assembler.register(Deplacements, requires=[Config,Log])
        else:
            Deplacements = DeplacementsSerie
            self.assembler.register(Deplacements, requires=[Serie,Config,Log])
        
        #enregistrement du service robot
        self.assembler.register(Robot, requires=[Deplacements,Config,Log])
        
    def get_service(self,type):
        return self.assembler.provide(type)
        