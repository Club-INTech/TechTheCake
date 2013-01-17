from time import sleep,time
from math import pi
from outils_maths.point import Point

class Script:
    """
    classe mère des scripts
    se charge des dépendances
    """
    def set_dependencies(self, robot, robotChrono, hookGenerator, rechercheChemin, config, log):
        """
        Gère les services nécessaires aux scripts. On n'utilise pas de constructeur.
        """
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.config = config
        self.log = log
        
    def va_au_point(self,position):
        """
        Méthode pour atteindre un point de la carte après avoir effectué une recherche de chemin.
        Le chemin n'est pas recalculé s'il a été exploré récemment.
        """
        def calcule_chemin(position):
            self.dernierChemin = self.rechercheChemin.get_chemin(Point(self.robot.x,self.robot.y),position)
            self.dateDernierChemin = time()
        try:
            if self.dernierChemin[-1] != position or time() - self.dateDernierChemin > self.config["duree_peremption_chemin"]:
                #le chemin est périmé et doit être recalculé
                calcule_chemin(position)
        except:
            #le chemin n'a jamais été calculé
            calcule_chemin(position)
        self.robot.suit_chemin(self.dernierChemin)

    def agit(self):
        """
        L'appel script.agit() effectue vraiment les instructions contenues dans execute().
        C'est à dire : envoi de trames sur la série, ou utilisation du simulateur.
        """
        self.robot = self.robotVrai
        self.execute()
        
    def calcule(self):
        """
        L'appel script.calcule() retourne la durée estimée des actions contenues dans execute().
        """
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.robot.maj_x_y_o(self.robotVrai.x, self.robotVrai.y, self.robotVrai.orientation)
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
            self.robot.actionneurs.enfoncer_bougie()
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
        
        
class ScriptTestRecalcul(Script):
    
    def execute(self):
        self.va_au_point(Point(0,300))
        self.va_au_point(Point(-100,500))
        
