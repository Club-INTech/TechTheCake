#passage de la couleur
import builtins

import os,sys
import time #pour l'attente du lancement des threads

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine

#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#module d'injection de dépendances
import assemblage

#modules partagés avec le code du robot principal
import mutex
import read_ini
import deplacements
import serieReelle
import log
import hooks

#modules spécifiques pour le robot secondaire
import robot2.robot as robot
import robot2.capteurs as capteurs
import robot2.actionneurs as actionneurs
import robot2.comportement as comportement
import robot2.threads as threads
import robot2.com2principal as com2principal
import robot2.serie as serie
import robot2.serieSimulation as serieSimulation
import robot2.simulateur as simulateur

class Container:
    """
    Cette classe se charge de contenir une instance unique de chaque service nécessité (et demandé) par le code.
    Elle utilise la bibliothèque d'injection de dépendances Assemblage.
    Les services chargés dépendent de la configuration (simulation/série) et sont ensuite utilisés de manière transparente.
    """
    def __init__(self, env="match"):
        self.assembler = assemblage.Assembler()
        self.mutex = mutex.Mutex()
        self.env = env
        self._chargement_service()
        self.start_threads()
        
    def get_service(self,id):
        """
        Méthode de génération d'un service. Elle renvoie toujours la même instance d'un service, qui n'est construite qu'à la première demande.
        """
        #mutex pour éviter la duplication d'un service à cause d'un thread (danger !)
        with self.mutex:
            return self.assembler.provide(id)
        
    def _chargement_service(self):
        """
        Enregistrement des services
        """
        
        #enregistrement du container en tant que service
        def make_container(*dependencies):
            return self
        self.assembler.register("container", None, factory=make_container)
        
        #enregistrement du service de configuration
        def make_conf():
            conf = read_ini.Config()
            conf.set_chemin(chemin+"/config")
            conf["cartes_serie"] = conf["cartes_serie"].split(",")
            conf["cartes_simulation"] = conf["cartes_simulation"].split(",")
            if hasattr(builtins, "couleur_robot"):
                conf["couleur"] = builtins.couleur_robot
            return conf
        self.assembler.register("config",read_ini.Config,factory=make_conf)
        
        #utilisation du service de configuration pour la suite
        self.config = self.get_service("config")
        
        #enregistrement du service des logs
        def make_log(config):
            if self.env == "match":
                instanceLog = log.Log(self.config)
                instanceLog.set_chemin(chemin)
            else:
                instanceLog = log.LogTest()
            return instanceLog
        self.assembler.register("log", log.Log, requires = ["config"], factory=make_log)
        
        
        #### SERVICES POUR LA SÉRIE ####
        #service de la série réelle si besoin :
        if not self.config["cartes_serie"] == ['']:
            
            #série réelle, qui controle le robot. Utilisée dans le service `serie`.
            self.assembler.register("serieReelle", serieReelle.SerieReelle, requires=["log"])
        else:
            
            #service vide pour créer le service `serie`. Ne sera pas utilisé.
            def make_none():
                return None
            self.assembler.register("serieReelle", None, requires=[], factory=make_none)
            
        #service de la série simulée si besoin :
        if not self.config["cartes_simulation"] == ['']:
            
            #service du simulateur
            def make_simulateur(config):
                simulateurInstance = simulateur.Simulateur(config)
                return simulateurInstance.soap
            self.assembler.register("simulateur", simulateur.Simulateur, requires=["config"], factory=make_simulateur)
            
            #visualisation sur le simulateur pour le robot et la recherche de chemin
            self.assembler.register("robot", robot.RobotSimulation, requires=["simulateur","capteurs","actionneurs","deplacements","hookGenerator","config","log"])
        
            #série virtuelle, qui redirige vers le simulateur
            self.assembler.register("serieSimulation", serieSimulation.SerieSimulation, requires=["simulateur", "log"])
        else:
            
            #pas de visualisation sur le simulateur pour le robot et la recherche de chemin
            self.assembler.register("robot", robot.Robot, requires=["capteurs","actionneurs","deplacements","hookGenerator","config","log"])
            
            def make_none():
                return None
            #service vide pour créer le service `serie`. Ne sera pas utilisé.
            self.assembler.register("serieSimulation", None, requires=[], factory=make_none)
            
        #service générique de série, qui redirige vers le service approprié (série réelle ou simulée)
        self.assembler.register("serie", serie.Serie, requires=["serieReelle", "serieSimulation", "config", "log"])
            
        ################################
        
        #enregistrement du service des capteurs pour la série
        self.assembler.register("capteurs", capteurs.Capteurs, requires=["serie","config","log"])
        
        #enregistrement du service des actionneurs pour la série
        self.assembler.register("actionneurs", actionneurs.Actionneurs, requires=["serie","config","log"])
        
        #enregistrement du service des déplacements pour la série
        self.assembler.register("deplacements", deplacements.Deplacements, requires=["serie","config","log"])
        
        #enregistrement du service hookGenerator
        self.assembler.register("hookGenerator", hooks.HookGenerator, requires=["config","log"])
        
        #enregistrement du service de communication avec le robot principal
        self.assembler.register("com2principal", com2principal.Com2principal, requires=["config", "log", "config"])
        
        #enregistrement du service timer
        self.assembler.register("threads.timer", threads.ThreadTimer, requires=["log","config","robot","com2principal"])
        self.assembler.register("threads.position", threads.ThreadPosition, requires=["container"])
        
        #enregistrement du service de comportement du robot secondaire
        self.assembler.register("comportement", comportement.Comportement, requires=["threads.timer", "robot", "com2principal", "config", "log"])
        
    def start_threads(self):
        """
        Lancement des threads
        """
        def lancement_des_threads():
            threads.AbstractThread.stop_threads = False
            
            self.get_service("threads.timer").start()
            self.get_service("threads.position").start()
            
            #attente d'une première mise à jour pour la suite
            robot = self.get_service("robot")
            while not robot.pret:
                time.sleep(0.1)
        
        lancement_des_threads()
    
    def stop_threads(self):
        """
        Stoppage des threads lancés (fonction bloquante jusqu'à l'arrêt)
        """
        #envoi de l'ordre de fin aux threads
        threads.AbstractThread.stop_threads = True
        
        #attente de la fin du thread position
        position = self.get_service("threads.position")
        if position.is_alive():
            position.join()
         
        #attente de la fin du thread timer
        timer = self.get_service("threads.timer")
        if timer.is_alive():
            timer.join()
        
    def reset(self):
        """
        Supprime toutes les instances de service et relance le container
        """
        self.stop_threads()
        self.assembler.reset()
        self._chargement_service()
        self.start_threads()