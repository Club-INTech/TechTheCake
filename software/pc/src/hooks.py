from math import pi
from time import time
from outils_maths.point import Point

_tolerance_angle_radians = 0.2

class Hook:
    """
    Classe mère des Hooks.
    elle stocke en attribut le callback (action à effectuer), ses paramètres (dans args)
    et un booléen unique spécifiant si le hook ne doit etre executé qu'une seule fois (valeur par défaut)
    """
    def __init__(self, config, log):
        self._config = config
        self._log = log
        self._callbacks = []
        
    def __iadd__(self, callback):
        self._callbacks.append(callback)
        return self

    def declencher(self):
        for callback in self._callbacks:
            callback.appeler()
                
class Callback:
    
    def __init__(self, fonction, arguments, unique):
        self.fonction = fonction
        self.arguments = arguments
        self.unique = unique
        self.done = False
            
    def appeler(self):
        if not self.unique or not self.done:
            self.fonction(*self.arguments)
            self.done = True
    
class HookPosition(Hook):
    """
    Classe des Hooks ayant pour condition une position du robot sur la table.
    La méthode evaluate() effectue l'action (callback) si le robot est dans un disque de tolérance centré sur position.
    """
    def __init__(self, config, log, position, tolerance_mm):
        Hook.__init__(self, config, log)
        if self._config["couleur"] == "bleu":
            position.x *= -1
        self.position_hook = position
        self.tolerance_mm = tolerance_mm
        
    def evaluate(self, robotX, robotY, **useless):
        if (Point(robotX, robotY).distance(self.position_hook) <= self.tolerance_mm):
            self.declencher()
        
class HookOrientation(Hook):
    """
    Classe des Hooks ayant pour condition une orientation absolue du robot sur la table.
    La méthode evaluate() effectue l'action (callback) si l'orientation du robot est dans un arc de tolérance autour de orientation.
    """
    def __init__(self, config, log, orientation, unique, callback,*args):
        Hook.__init__(self, config, log)
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
        self.test = 20
        self.types = {"position": HookPosition, "orientation": HookOrientation}
        
    def get_hook(self, type, condition, callback,*args,unique=True):
        """
        Cette méthode retourne une instance de hook :
        - du type "position" ou "orientation" demandé
        - qui à la condition donnée (respectivement un point ou un angle)
        - execute la fonction ou méthode de callback
        - en lui passant les paramètres contenus dans args
        """
        return self.types[type](condition, unique, callback,*args)
        
    def hook_position(self, position, tolerance_mm=None):
        """
        Création d'un hook en position
        """
        if tolerance_mm == None:
            tolerance_mm = self.config["hooks_tolerance_mm"]
            
        return HookPosition(self.log, position, tolerance_mm)
        
    def callback(self, fonction, arguments=(), unique=True):
        return Callback(fonction, arguments, unique)
        
class HookGeneratorSimulation(HookGenerator):
    """
    Héritage du hook factory pour afficher les hooks sur le simulateur
    """
    def __init__(self, config, log, simulateur):
        HookGenerator.__init__(self, config, log)
        self.simulateur = simulateur
        
    def hook_position(self, position, tolerance_mm=None):
        hook = HookGenerator.hook_position(self, position, tolerance_mm)
        self.simulateur.drawPoint(position.x, position.y, "black", "hook")
        self.simulateur.drawCircle(position.x, position.y, hook.tolerance_mm, False, "black", "hook")
        return hook
