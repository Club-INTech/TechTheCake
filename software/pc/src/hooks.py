from math import pi
from time import time

_tolerance_distance_mm   = 20
_tolerance_angle_radians = 0.2

class Hook:
    """
    Classe mère des Hooks.
    elle stocke en attribut le callback (action à effectuer), ses paramètres (dans args)
    et un booléen unique spécifiant si le hook ne doit etre executé qu'une seule fois (valeur par défaut)
    """
    def __init__(self,unique,callback,args):
        #méthode à appeler
        self.callback = callback
        #arguments facultatifs pour le callback
        self.args = args
        self.unique = unique
        if self.unique:
            self.done = False
    
class HookPosition(Hook):
    """
    Classe des Hooks ayant pour condition une position du robot sur la table.
    La méthode evaluate() effectue l'action (callback) si le robot est dans un disque de tolérance centré sur position.
    """
    def __init__(self, position, unique, callback,*args):
        Hook.__init__(self,unique, callback,args)
        #point déclencheur
        self.position_hook = position
    def evaluate(self,robotX,robotY,**useless):
        if not self.unique or not self.done:
            if ((robotX - self.position_hook.x)**2 + (robotY - self.position_hook.y)**2 <= _tolerance_distance_mm**2):
                if self.unique:
                    self.done = True
                self.callback(*self.args)
        
class HookOrientation(Hook):
    """
    Classe des Hooks ayant pour condition une orientation absolue du robot sur la table.
    La méthode evaluate() effectue l'action (callback) si l'orientation du robot est dans un arc de tolérance autour de orientation.
    """
    def __init__(self, orientation, unique, callback,*args):
        Hook.__init__(self,unique, callback,args)
        #angle déclencheur
        self.orientation_hook = orientation
    def evaluate(self,robotOrientation,**useless):
        if not self.unique or not self.done:
            delta_angle = abs(robotOrientation - self.orientation_hook)%(2*pi)
            if (delta_angle > pi): delta_angle = (2*pi)-delta_angle
            if (delta_angle <= _tolerance_angle_radians):
                if self.unique:
                    self.done = True
                self.callback(*self.args)
            
class HookGenerator():
    """
    Cette classe est chargée en tant que service dans le container.
    Elle permet de générer un Hook du type souhaité dans n'importe quel module du dépot.
    """
    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.types = {"position":HookPosition,"orientation":HookOrientation}
        
    def get_hook(self, type, condition, callback,*args,unique=True):
        """
        Cette méthode retourne une instance de hook :
        - du type "position" ou "orientation" demandé
        - qui à la condition donnée (respectivement un point ou un angle)
        - execute la fonction ou méthode de callback
        - en lui passant les paramètres contenus dans args
        """
        return self.types[type](condition, unique, callback,*args)
        