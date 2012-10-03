
#importation de la configuration
from src.read_ini import Config,Constantes

#module d'injection de dépendances
from src.assemblage import assembler

#modules
from src.robot import Robot
from src.deplacements import Deplacements_simu, Deplacements_serie
from src.scripts import Script, Script_bougies

class Container:
    def __init__(self):
        self.assembler = assembler()
        
        #enregistrement du service de configuration
        def make_conf():
            conf = Config()
            conf.set_chemin("config")
            return conf
        self.assembler.register(Config,factory=make_conf)
        
        #utilisation du service de configuration pour la suite
        self.config = self.get_service(Config)
        
        #enregistrement du service des déplacements
        if (self.config["mode_simulateur"]):
            print("mode simulateur")
            Deplacements = Deplacements_simu
        else:
            print("mode série")
            Deplacements = Deplacements_serie
        self.assembler.register(Deplacements, requires=[Config])
        
        #enregistrement du service robot
        self.assembler.register(Robot, requires=[Deplacements,Config])
        
        #enregistrement des services de scripts
        self.assembler.register(Script, requires=[Robot,Config])
        self.assembler.register(Script_bougies, requires=[Robot,Config])
        
    def get_service(self,type):
        return self.assembler.provide(type)
        
        
container = Container()
script = container.get_service(Script_bougies)