import math
from outils_maths.point import Point
import abc
import copy

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
    def va_au_point(self, point_consigne, **useless):
        pass
    
    @abc.abstractmethod
    def arc_de_cercle(self, point_destination, hooks=[]):
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
        
    def places_disponibles(self, avant):
        """
        Renvoie le nombre de places disponibles sur un ascenceur
        """
        if avant:
            return self.config["nb_max_verre"] - self.nb_verres_avant
        else:
            return self.config["nb_max_verre"] - self.nb_verres_arriere

    def recuperer_verre(self, avant):
        """
        Lance la procédure de récupération d'un verre
        """
        if avant:
            self.nb_verres_avant += 1
        else:
            self.nb_verres_arriere += 1

###################################################################################################################
#####  CLASSE ROBOTCHRONO, permet de mesurer le temps d'une succession d'actions (utilisé dans Script.calcule() ###
###################################################################################################################
    
class RobotChrono(RobotInterface):
    """
    Vive sopal'INT!
    """
    def __init__(self, rechercheChemin, config, log):
        
        #services nécessaires
        self.config = config
        self.log = log
        self.rechercheChemin = rechercheChemin
        
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
        
    def maj_capacite_verres(self, avant, arriere):
        self.nb_verres_avant = avant
        self.nb_verres_arriere = arriere
        
    def reset_compteur(self):
        self.duree = 0
        
    def get_compteur(self):
        return self.duree
    
#############################################################
### MÉTHODES ÉQUIVALENTES AUX MÉTHODES PUBLIQUES DE ROBOT ###
#############################################################

    def stopper(self):
        pass
    
    def avancer(self, distance, hooks=[], pas_reessayer=False):
        """
        Fonction analogue à celle de robot. Avance. Si, si.
        """
        self.duree += abs (distance / self.vitesses_translation[self.vitesse_translation-1])
        self.x += distance*math.cos(self.orientation)
        self.y += distance*math.sin(self.orientation)
        
    def tourner(self, angle, forcer = False,hooks=[]):
        """
        Fonction analogue à celle de robot. Bah... ça tourne quoi. Il vous faut un desmath.sin?
        """
        self.duree += abs(angle / self.vitesses_rotation[self.vitesse_rotation-1])
        self.orientation = angle
        
        
    def suit_chemin(self, chemin, **useless):
        """
        Fonction analogue à celle de robot. Cette méthode parcourt un chemin déjà calculé. Elle appelle va_au_point() sur chaque point de la liste chemin.
        """
        for position in chemin:
            self.va_au_point(position)
            
    def recherche_de_chemin(self, position, recharger_table=False):
        """
        Méthode pour calculer rapidement (algorithme A*) le temps mis pour atteindre un point de la carte après avoir effectué une recherche de chemin.
        """
        if recharger_table:
            self.rechercheChemin.retirer_obstacles_dynamiques()
            self.rechercheChemin.charge_obstacles()
            self.rechercheChemin.prepare_environnement_pour_a_star()
        
        depart = Point(self.x,self.y)
        arrivee = position.copy()
        if self.config["couleur"] == "bleu":
            arrivee.x *= -1
        chemin = self.rechercheChemin.cherche_chemin_avec_a_star(depart, arrivee)
        self.suit_chemin(chemin)
        
    def va_au_point(self, point_consigne, hooks=[], virage_initial=False):
        delta_x = point_consigne.x-self.x
        delta_y = point_consigne.y-self.y
        distance = round(math.sqrt(delta_x**2 + delta_y**2),2)
        angle = round(math.atan2(delta_y,delta_x),4)
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
        
    def places_disponibles(self, avant):
        pass

    def recuperer_verre(self, avant):
        pass

