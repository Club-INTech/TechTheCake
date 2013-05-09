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
import mutex

#module pour les threads
import threads

#modules -> services
import read_ini
import robot
import robotChrono
import deplacements
import capteurs
import laser
import actionneurs
import serie 
import serieReelle
import serieSimulation
import table
import recherche_de_chemin.rechercheChemin as rechercheChemin
import scripts
import strategie
import log
import hooks
import filtrage
import simulateur
import son

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
            if len(sys.argv) >= 2:
                conf["couleur"] = "rouge" if sys.argv[1] == "r" else "bleu"
            if len(sys.argv) >= 3:
                conf["case_depart_principal"] = int(sys.argv[2])
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
        
        #demande éventuelle de sudo avant de lancer les threads
        self.get_service("log")
        
        
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
        if not self.config["cartes_simulation"] == [''] or self.config["simulation_table"]:
            
            #service du simulateur
            def make_simulateur(config):
                simulateurInstance = simulateur.Simulateur(config)
                return simulateurInstance.soap
            self.assembler.register("simulateur", simulateur.Simulateur, requires=["config"], factory=make_simulateur)
            
            #visualisation sur le simulateur pour la table, le robot et la recherche de chemin
            self.assembler.register("table", table.TableSimulation, requires=["simulateur","config","log"])
            self.assembler.register("robot", robot.RobotSimulation, requires=["simulateur","capteurs","actionneurs","deplacements","rechercheChemin","hookGenerator","table","son","config","log"])
            if self.config["affichage_segments"]:
                self.assembler.register("rechercheChemin", rechercheChemin.RechercheCheminSimulation, requires=["simulateur", "table","config","log"])
            else:
                self.assembler.register("rechercheChemin", rechercheChemin.RechercheChemin, requires=["table","config","log"])
        
            #série virtuelle, qui redirige vers le simulateur
            self.assembler.register("serieSimulation", serieSimulation.SerieSimulation, requires=["simulateur", "table", "log"])
        else:
            
            #pas de visualisation sur le simulateur pour la table, le robot et la recherche de chemin
            self.assembler.register("table", table.Table, requires=["config","log"])
            self.assembler.register("robot", robot.Robot, requires=["capteurs","actionneurs","deplacements","rechercheChemin","hookGenerator","table","son","config","log"])
            self.assembler.register("rechercheChemin", rechercheChemin.RechercheChemin, requires=["table","config","log"])
            
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
        
        #enregistrement du service laser pour la série
        self.assembler.register("laser", laser.Laser, requires=["robot","serie","config","log"])
        
        #enregistrement du service de filtrage
        self.assembler.register("filtrage", filtrage.FiltrageLaser, requires=["config"])
        
        #enregistrement du service robotChrono
        self.assembler.register("robotChrono", robotChrono.RobotChrono, requires=["rechercheChemin", "actionneurs", "config", "log"])
        
        #enregistrement du service hookGenerator
        self.assembler.register("hookGenerator", hooks.HookGenerator, requires=["config","log"])
        
        #enregistrement du service son
        self.assembler.register("son", son.Son, requires=["config", "log"])

        #enregistrement du service timer
        self.assembler.register("threads.timer", threads.ThreadTimer, requires=["container"])
        self.assembler.register("threads.position", threads.ThreadPosition, requires=["container"])
        self.assembler.register("threads.capteurs", threads.ThreadCapteurs, requires=["container"])
        self.assembler.register("threads.laser", threads.ThreadLaser, requires=["container"])
        self.assembler.register("threads.bougies", threads.ThreadCouleurBougies, requires=["container"])

        
        #enregistrement du service d'instanciation des scripts
        def make_scripts(*dependencies):
            scriptManager = scripts.ScriptManager(*dependencies)
            return scriptManager.scripts
            
        self.assembler.register("scripts", scripts.ScriptManager, requires=["robot", "robotChrono", "hookGenerator", "table", "config", "log", "threads.timer"], factory=make_scripts)
        
        #enregistrement du service de stratégie
        self.assembler.register("strategie", strategie.Strategie, requires=["scripts", "rechercheChemin", "table", "threads.timer", "config", "log", "robot", "son"])
        
    def start_threads(self):
        """
        Lancement des threads
        """
        def lancement_des_threads():
            threads.AbstractThread.stop_threads = False
            
            self.get_service("threads.timer").start()
            self.get_service("threads.position").start()
            self.get_service("threads.capteurs").start()
            self.get_service("threads.bougies").start()
            
            if self.config["lasers_demarrer_thread"]:
                self.get_service("threads.laser").start()
            
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
         
        #attente de la fin du thread capteurs
        capteurs = self.get_service("threads.capteurs")
        if capteurs.is_alive():
            capteurs.join()
            
        #attente de la fin du thread timer
        timer = self.get_service("threads.timer")
        if timer.is_alive():
            timer.join()
            
        #attente de la fin du thread laser
        if self.config["lasers_demarrer_thread"]:
            laser = self.get_service("threads.laser")
            if laser.is_alive():
                laser.join()
            
        #attente de la fin du thread bougies
        bougies = self.get_service("threads.bougies")
        if bougies.is_alive():
            bougies.join()
        
    def reset(self):
        """
        Supprime toutes les instances de service et relance le container
        """
        self.stop_threads()
        self.assembler.reset()
        self._chargement_service()
        self.start_threads()
        
