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
    def avancer(self, distance, **useless):
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
    def actionneurs_bougie(self, en_haut, angle):
        pass
    
    @abc.abstractmethod
    def actionneur_cadeau(self, angle):
        pass
            
    @abc.abstractmethod
    def gonflage_ballon(self):
        pass
    
    @abc.abstractmethod
    def actionneurs_ascenseur(self, avant, position):
        pass
            
    @abc.abstractmethod
    def altitude_ascenseur(self, avant, hauteur):
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
            
    def deposer_pile(self, avant):
        """
        Indique au robot que l'un de ses ascenceurs est désormais vide
        """
        if avant:
            self.nb_verres_avant = 0
        else:
            self.nb_verres_arriere = 0
            
    def marche_arriere_est_plus_rapide(self, point_consigne, orientation_finale_voulue=None):
        """
        Retourne un booléen indiquant si la marche arrière fait gagner du temps pour atteindre le point consigne. 
        On évite ainsi d'implémenter une marche arrière automatique et on laisse la main aux scripts.
        """
        
        point_consigne = point_consigne.copy() #appliquer la symétrie ne doit pas modifier ce point !
        
        if orientation_finale_voulue is None:
            orientation_finale_voulue = self.orientation
        elif self.effectuer_symetrie and self.config["couleur"] == "bleu":
            orientation_finale_voulue = math.pi - orientation_finale_voulue
            
        if self.effectuer_symetrie and self.config["couleur"] == "bleu":
            point_consigne.x *= -1
            
        delta_x = point_consigne.x - self.x
        delta_y = point_consigne.y - self.y
        ecart_relatif = math.atan2(delta_y,delta_x) - orientation_finale_voulue
        if ecart_relatif > math.pi: ecart_relatif -= 2*math.pi
        elif ecart_relatif <= -math.pi: ecart_relatif += 2*math.pi
        
        return (ecart_relatif > math.pi/2 or ecart_relatif < -math.pi/2)
    
    def actionneur_cadeaux_sorti(self):
        return self.actionneurs.actionneur_cadeaux_actif
        
    def actionneur_bougies_sorti(self):
        return self.actionneurs.actionneur_bougies_actif
        
###################################################################################################################
#####  CLASSE ROBOTCHRONO, permet de mesurer le temps d'une succession d'actions (utilisé dans Script.calcule() ###
###################################################################################################################
    
class RobotChrono(RobotInterface):
    """
    Vive sopal'INT!
    """
    def __init__(self, rechercheChemin, actionneurs, config, log):
        
        #services nécessaires
        self.rechercheChemin = rechercheChemin
        self.actionneurs = actionneurs
        self.config = config
        self.log = log
        
        self.duree = 0
        
        #tableau des 3 vitesses de translation 1,2,3 , en mm/sec
        self.vitesses_translation = [138,358,446]
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
    
    def avancer(self, distance, **useless):
        """
        Fonction analogue à celle de robot. Avance. Si, si.
        """
        if self.vitesse_translation < 5:
            self.duree += abs (distance / self.vitesses_translation[self.vitesse_translation-1])
        else:
            self.duree += abs (distance / self.vitesse_translation*(self.vitesses_translation[1]/100))
        self.x += distance*math.cos(self.orientation)
        self.y += distance*math.sin(self.orientation)
        
    def tourner(self, angle, **useless):
        """
        Fonction analogue à celle de robot. Bah... ça tourne quoi. Il vous faut un desmath.sin? # J'ai pas compris lol.
        """
        if self.effectuer_symetrie:
            if self.config["couleur"] == "bleu":
                angle = math.pi - angle
                
        if self.vitesse_rotation < 5:
            self.duree += abs(angle / self.vitesses_rotation[self.vitesse_rotation-1])
        else:
            self.duree += abs(angle / self.vitesse_rotation*(self.vitesses_rotation[1]/100))
        
        self.orientation = angle
        
        
    def suit_chemin(self, chemin, hooks=[], marche_arriere_auto=True, symetrie_effectuee=False):
        """
        Fonction analogue à celle de robot. Cette méthode parcourt un chemin déjà calculé. Elle appelle va_au_point() sur chaque point de la liste chemin.
        """
        for position in chemin:
            if marche_arriere_auto:
                self.marche_arriere = self.marche_arriere_est_plus_rapide(position)
            self.va_au_point(position, hooks, symetrie_effectuee=symetrie_effectuee)
            
    def recherche_de_chemin(self, arrivee, recharger_table=False, renvoie_juste_chemin=False):
        """
        Méthode pour calculer rapidement (algorithme A*) le temps mis pour atteindre un point de la carte après avoir effectué une recherche de chemin.
        """
        
        arrivee = arrivee.copy() #appliquer la symétrie ne doit pas modifier ce point !
        
        if recharger_table:
            self.rechercheChemin.retirer_obstacles_dynamiques()
            self.rechercheChemin.charge_obstacles(avec_verres_entrees=True)
            self.rechercheChemin.prepare_environnement_pour_a_star()
        
        depart = Point(self.x,self.y)
        if self.effectuer_symetrie and self.config["couleur"] == "bleu":
            arrivee.x *= -1
        chemin = self.rechercheChemin.cherche_chemin_avec_a_star(depart, arrivee)
        
        if renvoie_juste_chemin:
            return chemin
            
        self.suit_chemin(chemin, symetrie_effectuee=True)
        
    def va_au_point(self, point_consigne, hooks=[], trajectoire_courbe=False, nombre_tentatives=2, retenter_si_blocage=True, symetrie_effectuee=False, sans_lever_exception=False):
        
        point_consigne = point_consigne.copy() #appliquer la symétrie ne doit pas modifier ce point !
        
        if self.effectuer_symetrie and not symetrie_effectuee:
            if self.config["couleur"] == "bleu":
                point_consigne.x *= -1
                
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
        
    def actionneurs_bougie(self, en_haut, angle):
        pass
    
    def actionneur_cadeau(self, angle):
        pass
            
    def gonflage_ballon(self):
        pass
        
    def places_disponibles(self, avant):
        pass

    def actionneurs_ascenseur(self, avant, position):
        pass

    def altitude_ascenseur(self, avant, hauteur):
        pass

    def recuperer_verre(self, avant):
        pass

    def deposer_pile(self, avant):
        pass

    def deposer_pile_combo(self, avant):
        pass

