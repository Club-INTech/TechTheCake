import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine

#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#module d'injection de dépendances
from assemblage import assembler
from mutex import Mutex

#modules -> services
from read_ini import Config
from robot import *
from robotChrono import RobotChrono
from deplacements import DeplacementsSimulateur, DeplacementsSerie
from capteurs import CapteursSerie, CapteursSimulateur
from serie import Serie
from table import TableSimulateur
from suds.client import Client
from scripts import Script, ScriptBougies
from log import Log

class Container:
    def __init__(self):
        self.assembler = assembler()
        self.mutex = Mutex()
        
        #enregistrement du service de configuration
        def make_conf():
            conf = Config()
            conf.set_chemin(chemin+"/config")
            return conf
        self.assembler.register("config",Config,factory=make_conf)
        
        #utilisation du service de configuration pour la suite
        self.config = self.get_service("config")
        
        #enregistrement du service des logs
        def make_log(config):
            log = Log(self.config)
            log.set_chemin(chemin)
            return log
        self.assembler.register("log", Log, requires = ["config"], factory=make_log)
        
        #services différents en fonction du mode simulateur on/off :
        if (self.config["mode_simulateur"]):
            #enregistrement du service Simulateur
            def make_simu():
                #client SOAP pour le simulateur
                client=Client("http://localhost:8090/INTechSimulator?wsdl")
                #initialisation de la table
                client.service.reset()
                client.service.setTableDimension(self.config["table_x"],self.config["table_y"])
                client.service.defineCoordinateSystem(1,0,0,-1,self.config["table_x"]/2,self.config["table_y"])
                #déclaration du robot
                client.service.defineRobot({"list":[{"float":[-200.,-200.]},{"float":[-200.,200.]},{"float":[200.,200.]},{"float":[200.,-200.]}]})
                #déclaration d'un robot adverse
                client.service.addEnemy(30,"black")
                return client.service
                
            self.assembler.register("simulateur",  None, factory=make_simu)
            #enregistrement du service des capteurs pour le simulateur
            self.assembler.register("capteurs",CapteursSimulateur, requires=["simulateur","config","log"])
            #enregistrement du service des déplacements pour le simulateur
            self.assembler.register("deplacements",DeplacementsSimulateur, requires=["simulateur","config","log"])
            
            #enregistrement du service donnant des infos sur la table
            self.assembler.register("table", TableSimulateur, requires=["config","log"])
            
            
        else:
            #enregistrement du service Serie
            self.assembler.register("serie", Serie, requires = ["log"])
            #enregistrement du service des capteurs pour la série
            self.assembler.register("capteurs",CapteursSerie, requires=["serie","config","log"])
            #enregistrement du service des déplacements pour la série
            self.assembler.register("deplacements",DeplacementsSerie, requires=["serie","config","log"])
        
        #enregistrement du service robot
        self.assembler.register("robot", Robot, requires=["capteurs","deplacements","config","log"])
        
        #enregistrement du service robotChrono
        self.assembler.register("robotChrono", RobotChrono, requires=["log"])
        
        """
        
        
        #enregistrement du service de recherche de chemin
        self.assembler.register("recherche_chemin", RechercheChemin, requires=["table","log"])
        
        #enregistrement du service de scripts
        self.assembler.register("script", Script, requires=["robot","config","log"])
        """
        
    def get_service(self,id):
        #mutex pour éviter la duplication d'un service à cause d'un thread (danger !)
        with self.mutex:
            return self.assembler.provide(id)
        