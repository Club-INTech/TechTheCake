from math import sqrt,atan2, cos, sin
import abc

##################################################################################################################
#####  CLASSE ROBOTINTERFACE, permet de vérifier l'équivalence des méthodes publiques de Robot et RobotChrono. ###
##################################################################################################################

class RobotInterface(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def stopper(self):
        pass
    
    @abc.abstractmethod
    def avancer(self, distance):
        pass
        
    @abc.abstractmethod
    def tourner(self, angle, forcer = False,hooks=[]):
        pass
        
    @abc.abstractmethod
    def suit_chemin(self, chemin, **useless):
        pass
            
    @abc.abstractmethod
    def va_au_point(self,consigne_x,consigne_y,**useless):
        pass
    
    @abc.abstractmethod
    def arc_de_cercle(self,xM,yM,hooks=[]):
        pass
        
    @abc.abstractmethod
    def set_vitesse_translation(self, valeur):
        pass
    
    @abc.abstractmethod
    def set_vitesse_rotation(self, valeur):
        pass
        
    @abc.abstractmethod
    def traiter_bougie(self,id,enHaut):
        pass
            
    @abc.abstractmethod
    def initialiser_bras_bougie(self,enHaut) : 
        pass

    @abc.abstractmethod
    def rentrer_bras_bougie(self) : 
        pass
    
    @abc.abstractmethod
    def ouvrir_cadeau(self):
        pass
        
    @abc.abstractmethod
    def fermer_cadeau(self):
        pass
        
    @abc.abstractmethod
    def gonflage_ballon(self):
        pass
    
###################################################################################################################
#####  CLASSE ROBOTCHRONO, permet de mesurer le temps d'une succession d'actions (utilisé dans Script.calcule() ###
###################################################################################################################
    
class RobotChrono(RobotInterface):
    """
    Vive sopal'INT!
    """
    def __init__(self, log):
        
        self.log = log
        self.duree = 0
        
        #tableau des 3 vitesses de translation 1,2,3 , en mm/sec
        self.vitesses_translation = [100,300,500]
        #tableau des 3 vitesses de rotation 1,2,3 , en radian/sec
        self.vitesses_rotation = [0.7,1.5,3.0]
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #valeur par défaut
        self.effectuer_symetrie = True
        self.marche_arriere = True
        
    def maj_x_y_o(self,x,y,orientation):
        self.x = x
        self.y = y
        self.orientation = orientation
        
    def reset_compteur(self):
        self.duree = 0
        
    def get_compteur(self):
        return self.duree
    
#############################################################
### MÉTHODES ÉQUIVALENTES AUX MÉTHODES PUBLIQUES DE ROBOT ###
#############################################################

    def stopper(self):
        pass
    
    def avancer(self, distance, hooks=[], pasReessayer=False):
        """
        Fonction analogue à celle de robot. Avance. Si, si.
        """
        self.duree += distance / self.vitesses_translation[self.vitesse_translation-1]
        self.x += distance*cos(self.orientation)
        self.y += distance*sin(self.orientation)
        
    def tourner(self, angle, forcer = False,hooks=[]):
        """
        Fonction analogue à celle de robot. Bah... ça tourne quoi. Il vous faut un dessin?
        """
        self.duree += angle / self.vitesses_rotation[self.vitesse_rotation-1]
        self.orientation = angle
        
        
    def suit_chemin(self, chemin, **useless):
        """
        Fonction analogue à celle de robot. Cette méthode parcourt un chemin déjà calculé. Elle appelle va_au_point() sur chaque point de la liste chemin.
        """
        for position in chemin:
            self.va_au_point(position.x, position.y)
            
    def va_au_point(self,consigne_x,consigne_y,**useless):
        delta_x = consigne_x-self.x
        delta_y = consigne_y-self.y
        distance = round(sqrt(delta_x**2 + delta_y**2),2)
        angle = round(atan2(delta_y,delta_x),4)
        self.tourner(angle)
        self.avancer(distance)
    
    def arc_de_cercle(self,xM,yM,hooks=[]):
        #TODO
        pass
        
    def set_vitesse_translation(self, valeur):
        """
        Fonction analogue à celle de robot. modifie la vitesse de translation du robot et adapte les constantes d'asservissement
        """
        self.vitesse_translation = int(valeur)
    
    def set_vitesse_rotation(self, valeur):
        """
        Fonction analogue à celle de robot. modifie la vitesse de rotation du robot et adapte les constantes d'asservissement
        """
        self.vitesse_rotation = int(valeur)
        
    def traiter_bougie(self,id,enHaut):
        pass
            
    def initialiser_bras_bougie(self,enHaut) : 
        pass

    def rentrer_bras_bougie(self) : 
        pass
    
    def ouvrir_cadeau(self):
        pass
        
    def fermer_cadeau(self):
        pass
        
    def gonflage_ballon(self):
        pass
