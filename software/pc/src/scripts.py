from time import sleep
from math import pi
from outils_maths.point import Point

class Script:
    """
    classe mère des scripts
    se charge des dépendances
    """
    def set_dependencies(self, robot, robotChrono, hookGenerator, log, config):
        
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.log = log
        self.config = config

    def agit(self):
        self.robot = self.robotVrai
        self.execute()
        
    def calcule(self):
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.execute()
        return self.robot.get_compteur()
    
        
class ScriptBougies(Script):
    """
    exemple de classe de script pour les bougies
    hérite de la classe mère Script
    """
    
    def __init__(self):
        #dictionnaire définissant les bougies actives ou non
        self.bougies = {"bougie1" : False, "bougie2" : True, "bougie3" : True, "bougie4" : True}
        
    def execute(self):
	    #self.robot.va_au_point(#,#)
	    if(self.robot.capteurCouleur.lire_couleur() == self.robot.couleur):
            self.robot.actionneur.enfoncer_bougie()
            self.robot.actionneurs.initialiser_bras_bougie()
		           
    
class ScriptTestHooks(Script):
    
    def execute(self):
            
        def aFaire(texte):
            print("appel du callback : "+texte)
            
        hooks = []
        hooks.append(self.hookGenerator.get_hook("position", Point(910,300), aFaire, "lapin", unique = False))
        hooks.append(self.hookGenerator.get_hook("orientation", pi, aFaire, "chèvre"))
        
        self.robot.avancer(300,hooks)
        self.robot.tourner(pi/2,hooks)
        self.robot.avancer(500,hooks)
        
        
class ScriptTestCadeaux(Script):
    
    def execute(self):
        
        self.robot.va_au_point(1150,250)

        hooks = []
        hooks.append(self.hookGenerator.get_hook("position", Point(1000,250), self.robot.actionneurs.ouvrir_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(980,250), self.robot.actionneurs.fermer_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(800,250), self.robot.actionneurs.ouvrir_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(780,250), self.robot.actionneurs.fermer_cadeau))
          
        self.robot.avancer(600,hooks)
