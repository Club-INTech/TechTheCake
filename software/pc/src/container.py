import os,sys

from math import pi #pour l'orientation initiale du simulateur
from time import sleep #pour l'attente du lancement des threads

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine

#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#module d'injection de dépendances
from assemblage import assembler
from mutex import Mutex

from tests import ContainerTest

#module pour les threads
from threading import Thread
#fonctions pour les thread de mises à jour
from thread_MAJ import fonction_MAJ
from thread_capteurs import fonction_capteurs
from thread_lasers import fonction_laser

#modules -> services
from read_ini import Config
from robot import Robot
from robotChrono import RobotChrono
from deplacements import Deplacements
from capteurs import Capteurs
from laser import *
from actionneurs import Actionneurs
from serie import Serie
from serieSimulation import SerieSimulation
from table import Table, TableSimulation
from timer import Timer
from recherche_de_chemin.rechercheChemin import RechercheChemin
from scripts import ScriptManager
from strategie import Strategie
from log import Log
from hooks import HookGenerator
from filtrage import FiltrageLaser
from simulateur import Simulateur

class Container:
    """
    Cette classe se charge de contenir une instance unique de chaque service nécessité (et demandé) par le code.
    Elle utilise la bibliothèque d'injection de dépendances Assemblage.
    Les services chargés dépendent de la configuration (simulation/série) et sont ensuite utilisés de manière transparente.
    """
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
            def make_simulateur(config):
                simulateur = Simulateur(config)
                return simulateur.soap
            self.assembler.register("simulateur", Simulateur, requires=["config"], factory=make_simulateur)
            self.assembler.register("serie", SerieSimulation, requires=["simulateur","log"])
            self.assembler.register("table", TableSimulation, requires=["simulateur","config","log"])
        else:
            self.assembler.register("serie", Serie, requires=["log"])
            self.assembler.register("table", Table, requires=["config","log"])
            
        #enregistrement du service des capteurs pour la série
        self.assembler.register("capteurs", Capteurs, requires=["serie","config","log"])
        
        #enregistrement du service des actionneurs pour la série
        self.assembler.register("actionneurs", Actionneurs, requires=["serie","config","log"])
        
        #enregistrement du service des déplacements pour la série
        self.assembler.register("deplacements", Deplacements, requires=["serie","config","log"])
        
        #enregistrement du service laser pour la série
        self.assembler.register("laser", Laser, requires=["robot","serie","config","log"])
        
        #enregistrement du service robot
        self.assembler.register("robot", Robot, requires=["capteurs","actionneurs","deplacements","config","log","table"])
        
        #enregistrement du service robotChrono
        self.assembler.register("robotChrono", RobotChrono, requires=["log"])
        
        #enregistrement du service timer
        self.assembler.register("timer", Timer, requires=["log","config","robot","table","capteurs"])

        #enregistrement du service de recherche de chemin
        self.assembler.register("rechercheChemin", RechercheChemin, requires=["table","config","log"])
        
        #enregistrement du service de génération des hooks
        self.assembler.register("hookGenerator", HookGenerator, requires=["config","log"])
        
        #enregistrement du service d'instanciation des scripts
        def make_scripts(*dependencies):
            scriptManager = ScriptManager(*dependencies)
            return scriptManager.scripts
        self.assembler.register("scripts", ScriptManager, requires=["config", "log", "robot", "robotChrono", "hookGenerator", "rechercheChemin", "table"], factory = make_scripts)
        
        #enregistrement du service de stratégie
        self.assembler.register("strategie", Strategie, requires=["robot", "scripts", "rechercheChemin", "table", "timer", "config", "log"])
        
        #enregistrement du service de filtrage
        self.assembler.register("filtrage", FiltrageLaser, requires=["config"])

        #lancement des threads
        self._start_threads()
        
        
    def _start_threads(self):
        """
        Le lancement des thread (et leur attente d'une initialisation) est gérée ici.
        """
        #fonction qui lance les threads
        def lancement_des_threads():
            #lancement des threads de mise à jour
            thread_MAJ = Thread(None, fonction_MAJ, None, (), {"container":self})
            thread_MAJ.start()
            
            #thread des capteurs
            thread_capteurs = Thread(None, fonction_capteurs, None, (), {"container":self})
            thread_capteurs.start()
            
            #thread des lasers
            if self.config["lasers_demarrer_thread"]:
                thread_lasers = Thread(None, fonction_laser, None, (), {"container":self})
                thread_lasers.start()
                
            timer = self.get_service("timer")
            thread_service_timer = Thread(None, timer.thread_timer, None, (), {})
            thread_service_timer.start()
            #attente d'une première mise à jour pour la suite
            robot = self.get_service("robot")
            while not robot.pret:
                sleep(0.1)
        
        #conditions sur le lancement des threads
        if self.config["mode_simulateur"]:
            #si on est en mode simulateur...
            lancement_des_threads()
        else:
            #...ou si l'asservissement en série est présent
            serie = self.get_service("serie")
            if hasattr(serie.peripheriques["asservissement"],'serie'):
                lancement_des_threads()
                
                
    def get_service(self,id):
        """
        Méthode de génération d'un service. Elle renvoie toujours la même instance d'un service, qui n'est construite qu'à la première demande.
        """
        #mutex pour éviter la duplication d'un service à cause d'un thread (danger !)
        with self.mutex:
            return self.assembler.provide(id)
        
