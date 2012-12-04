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
from robotChrono import RobotChrono
from deplacements import DeplacementsSimulateur, DeplacementsSerie
from capteurs import CapteursSerie, CapteursSimulateur
from serie import Serie
from suds.client import Client
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
                client=Client("http://localhost:8090/INTechSimulator?wsdl")
                #initialisation de la table TODO : prendre les valeurs dans Table
                client.service.reset()
                client.service.setTableDimension(3000,2000)
                client.service.defineCoordinateSystem(1,0,0,-1,1500,2000)
                client.service.defineRobot({"list":[{"float":[-200.,-200.]},{"float":[-200.,200.]},{"float":[200.,200.]},{"float":[200.,-200.]}]})
                client.service.addSensor(0,{"list":[{"int":[0,-400]},{"int":[-135.,-1100.]},{"int":[135,-1100]}]}) #nombre pair: infrarouge. Nombre impair: ultrasons
                client.service.addSensor(2,{"list":[{"int":[0,400]},{"int":[-135.,1100.]},{"int":[135,1100]}]})
                client.service.addSensor(1,{"list":[{"int":[0,-400]},{"int":[-600.,-1600.]},{"int":[600,-1600]}]})
                client.service.addSensor(3,{"list":[{"int":[0,400]},{"int":[-600.,1600.]},{"int":[600,1600]}]})
                client.service.setRobotAngle(0)
                client.service.setRobotPosition(-1200,300)
                client.service.addEnemy(30,"black")
                return client.service
            self.assembler.register("simulateur",  None, factory=make_simu)
            
            #enregistrement du service des déplacements pour le simulateur
            self.assembler.register("deplacements",DeplacementsSimulateur, requires=["simulateur","config","log"])
            #enregistrement du service des capteurs pour le simulateur
            self.assembler.register("capteurs",CapteursSimulateur, requires=["simulateur","config","log"])
            
        else:
            #enregistrement du service Serie
            self.assembler.register("serie", Serie, requires = ["log"])
            ##enregistrement du service des déplacements pour la série
            #self.assembler.register("deplacements",DeplacementsSerie, requires=["serie","config","log"])
            ##enregistrement du service des capteurs pour la série
            #self.assembler.register("capteurs",CapteursSerie, requires=["serie","config","log"])
        
        ##enregistrement du service robot
        #self.assembler.register("robot", Robot, requires=["deplacements","capteurs","config","log"])
        
        ##enregistrement du service robotChrono
        #self.assembler.register("robotChrono", RobotChrono, requires=["log"])
        
        """
        #enregistrement du service donnant des infos sur la table
        self.assembler.register("table", Table, requires=["config","log"])
        
        #enregistrement du service de recherche de chemin
        self.assembler.register("recherche_chemin", RechercheChemin, requires=["table","log"])
        
        #enregistrement du service de scripts
        self.assembler.register("script", Script, requires=["robot","config","log"])
        """
        
    def get_service(self,id):
        return self.assembler.provide(id)
        
