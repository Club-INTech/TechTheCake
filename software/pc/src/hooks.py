from math import pi
from time import time
from outils_maths.point import Point
import tests

_tolerance_distance_mm   = 20
_tolerance_angle_radians = 0.2

class Hook:
    """
    Classe mère des Hooks.
    elle stocke en attribut le callback (action à effectuer), ses paramètres (dans args)
    et un booléen unique spécifiant si le hook ne doit etre executé qu'une seule fois (valeur par défaut)
    """
    def __init__(self, log):
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
    def __init__(self, log, position):
        Hook.__init__(self, log)
        self.position_hook = position
        
    def evaluate(self, robotX, robotY, **useless):
        if (Point(robotX, robotY).distance(self.position_hook) <= _tolerance_distance_mm):
            self.declencher()
        
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
        
    def hook_position(self, position):
        return HookPosition(self.log, position)
        
    def callback(self, fonction, arguments=(), unique=True):
        return Callback(fonction, arguments, unique)
        
class HookGeneratorSimulation(HookGenerator):
    """
    Héritage du hook factory pour afficher les hooks sur le simulateur
    """
    def __init__(self, config, log, simulateur):
        HookGenerator.__init__(self, config, log)
        self.simulateur = simulateur
        
    def hook_position(self, position):
        self.simulateur.drawPoint(position.x, position.y, "black", "hook")
        self.simulateur.drawCircle(position.x, position.y, _tolerance_distance_mm, False, "black", "hook")
        return HookGenerator.hook_position(self, position)
        
        
class TestHook(tests.ContainerTest):
    
    def test_callbacks(self):
        
        # Création d'une fonction à appeler
        return_1 = False
        def fonction_test_1():
            nonlocal return_1
            return_1 = True
            
        # Création d'une fonction à appeler avec arguments
        return_2 = False
        def fonction_test_2(arg1, arg2):
            if arg1 == "test":
                nonlocal return_2
                return_2 = True
            
        # Création d'un hook
        self.factory = self.get_service("hookGenerator")
        hook = self.factory.hook_position(Point(0, 0))
        
        # Attachement d'un premier callback
        hook += self.factory.callback(fonction_test_1)
        
        # Attachement d'un second callback avec arguments
        hook += self.factory.callback(fonction_test_2, ("test", None))
        
        # Déclenchement du hook
        hook.declencher()
        
        # Vérification que les 2 callbacks ont été appelés
        self.assertTrue(return_1)
        self.assertTrue(return_2)
        
    def test_callbacks_unique(self):
        
        # Création d'une fonction à appeler une seule fois
        return_1 = 0
        def fonction_test_1():
            nonlocal return_1
            return_1 += 1
            
        # Création d'une fonction à appeler plusieurs fois
        return_2 = 0
        def fonction_test_2():
            nonlocal return_2
            return_2 += 1
            
        # Création d'un hook
        self.factory = self.get_service("hookGenerator")
        hook = self.factory.hook_position(Point(0, 0))
        
        # Attachement d'un premier callback
        hook += self.factory.callback(fonction_test_1, unique=True)
        
        # Attachement d'un second callback non unique
        hook += self.factory.callback(fonction_test_2, unique=False)
        
        # Déclenchement du hook
        hook.declencher()
        hook.declencher()
        hook.declencher()
        
        # Vérification que les 2 callbacks ont été appelés
        self.assertEqual(return_1, 1)
        self.assertTrue(return_2, 3)
        
