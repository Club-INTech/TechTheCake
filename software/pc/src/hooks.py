import math
from outils_maths.point import Point

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
    def __init__(self, config, log, position, tolerance_mm, effectuer_symetrie):
        Hook.__init__(self, config, log)
        self.position_hook = position
        self.tolerance_mm = tolerance_mm
        if effectuer_symetrie:
            self.position_hook.x *= -1
        
    def evaluate(self, robotX, robotY, **useless):
        if (Point(robotX, robotY).distance(self.position_hook) <= self.tolerance_mm):
            self.declencher()
        
class HookAngleGateau(Hook):
    """
    Classe des Hooks ayant pour condition le passage d'un angle de référence autour du gateau. 
    La méthode evaluate() effectue l'action (callback) si 
    le robot dépasse la ligne dirigée par `angle` 
    dans le sens `vers_x_croissant` (booléen)
    """
    def __init__(self, config, log, angle, vers_x_croissant):
        Hook.__init__(self, config, log)
        self.angle_hook = angle
        self.vers_x_croissant = vers_x_croissant
        
    def evaluate(self, robotX, robotY, **useless):
        erreur = math.atan2(robotY - 2000, robotX - 0) - self.angle_hook
        if (self.vers_x_croissant and erreur > 0) or (not self.vers_x_croissant and erreur < 0):
            self.declencher()
            
class HookDroiteVerticale(Hook):
    """
    Classe des Hooks ayant pour condition le passage d'une droite verticale de référence. 
    La méthode evaluate() effectue l'action (callback) si 
    le robot dépasse la ligne 
    dans le sens `vers_x_croissant` (booléen)
    """
    def __init__(self, config, log, posX, vers_x_croissant):
        Hook.__init__(self, config, log)
        self.posX = posX
        self.vers_x_croissant = vers_x_croissant
        
    def evaluate(self, robotX, **useless):
        if (self.vers_x_croissant and robotX > self.posX) or (not self.vers_x_croissant and robotX < self.posX):
            self.declencher()
            
class HookCapteurVerres(Hook):
    """
    Classe des Hooks ayant pour condition le déclenchement d'un des deux capteurs de verres
    La méthode evaluate() effectue l'action (callback) si le capteur est activé
    """
    def __init__(self, config, log, robot, avant):
        Hook.__init__(self, config, log)
        self.robot = robot
        self.avant = avant
        
    def evaluate(self, **useless):
        if self.robot.capteurs.verre_present(self.avant):
            self.declencher()


class HookGenerator():
    """
    Cette classe est chargée en tant que service dans le container.
    Elle permet de générer un Hook du type souhaité dans n'importe quel module du dépot.
    """
    def __init__(self, config, log):
        self.config = config
        self.log = log
        
    def hook_position(self, position, tolerance_mm=None, effectuer_symetrie=False):
        """
        Création d'un hook en position
        """
        if tolerance_mm == None:
            tolerance_mm = self.config["hooks_tolerance_mm"]
            
        return HookPosition(self.config, self.log, position, tolerance_mm, effectuer_symetrie)
        
    def hook_angle_gateau(self, angle, vers_x_croissant):
        """
        Création d'un hook de dépassement d'une droite autour du gateau
        """
        return HookAngleGateau(self.config, self.log, angle, vers_x_croissant)
        
    def hook_droite_verticale(self, posX, vers_x_croissant):
        """
        Création d'un hook de dépassement d'une droite verticale
        """
        return HookDroiteVerticale(self.config, self.log, posX, vers_x_croissant)

    def hook_capteur_verres(self, robot, avant):
        """
        Création d'un hook de détection de verre
        """
        return HookCapteurVerres(self.config, self.log, robot, avant)
        
    def callback(self, fonction, arguments=(), unique=True):
        return Callback(fonction, arguments, unique)
