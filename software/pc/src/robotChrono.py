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
    def correction_angle(self, angle):
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
    def arc_de_cercle(self, point_destination, hooks=[], nombre_tentatives=2):
        pass
        
    @abc.abstractmethod
    def set_vitesse_translation(self, vitesse):
        pass
    
    @abc.abstractmethod
    def set_vitesse_rotation(self, vitesse, rayon=None):
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

    def conventions_vitesse_translation(vitesse):
        """
        Retourne un pwm_max en fonction d'une convention de vitesse.
        """
        if vitesse == "entre_scripts":
            return 150#120
        elif vitesse == "recherche_verre":
            return 95#70
        elif vitesse == "depot_verre":
            return 90#60
        elif vitesse == "proche_gateau":
            return 100
        elif vitesse == "prudence_reglette":
            return 90#70
        elif vitesse == "arc_de_cercle":
            return 56#48
        elif vitesse == "arc_de_cercle_moyen":
            return 63#51
        elif vitesse == "arc_de_cercle_fort":
            return 72#54
        elif vitesse == "cadeaux":
            return 87
        elif vitesse == "recal_faible":
            return 90#60
        elif vitesse == "recal_forte":
            return 120
        else:
            raise Exception("string de vitesse translation inconnu ! (cf RobotInterface.conventions_vitesse_translation)")
        
    def conventions_vitesse_rotation(vitesse, rayon=None):
        """
        Retourne un pwm_max en fonction d'une convention de vitesse.
        """
        if vitesse == "entre_scripts":
            return 160#100
        elif vitesse == "recherche_verre":
            return 120
        elif vitesse == "depot_verre":
            return 120
        elif vitesse == "proche_gateau":
            return 140
        elif vitesse == "arc_de_cercle":
            #return int(max(118-0.21*(rayon-478), 30))
            return int(max(132-0.19*(rayon-478), 30))
        elif vitesse == "fin_arc":
            return 50
        elif vitesse == "cadeaux":
            return 140
        elif vitesse == "prudence_reglette":
            return 110
        elif vitesse == "recal_faible":
            return 120
        elif vitesse == "recal_forte":
            return 130
        else:
            raise Exception("string de vitesse rotation inconnu ! (cf RobotInterface.conventions_vitesse_rotation)")
        
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
        #self.log.warning("avancer de "+str(distance)+" à "+str(round(self.vitesse_translation,2))+"mm/s prend "+str(round(abs(distance / self.vitesse_translation),2))+" sec.")
        
        self.duree += abs(distance / self.vitesse_translation)
        self.x += distance*math.cos(self.orientation)
        self.y += distance*math.sin(self.orientation)
        
    def correction_angle(self, angle):
        pass
    
    def tourner(self, angle, **useless):
        """
        Fonction analogue à celle de robot. Bah... ça tourne quoi. Il vous faut un desmath.sin? # J'ai pas compris lol.
        """
        #self.log.warning("tourner à "+str(angle)+" à "+str(round(self.vitesse_rotation,2))+"rad/s prend "+str(round(abs(angle / self.vitesse_rotation),2))+" sec.")
        
        if self.effectuer_symetrie:
            if self.config["couleur"] == "bleu":
                angle = math.pi - angle
                
        self.duree += abs(angle / self.vitesse_rotation)
        
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
            self.rechercheChemin.prepare_environnement_pour_visilibity()
        
        depart = Point(self.x,self.y)
        if self.effectuer_symetrie and self.config["couleur"] == "bleu":
            arrivee.x *= -1
        chemin = self.rechercheChemin.cherche_chemin_avec_visilibity(depart, arrivee)
        
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
    
    def arc_de_cercle(self, point_destination, hooks=[], nombre_tentatives=2):
        """
        La durée de l'arc de cercle est calculée à partir du parcourt d'une abscisse curviligne.
        """
        
        delta_rx = 0 - self.x
        delta_ry = 2000 - self.y
        rayon = math.sqrt(delta_rx**2 + delta_ry**2)
        theta_r = math.atan2(delta_ry,delta_rx)
        
        delta_mx = 0 - point_destination.x
        delta_my = 2000 - point_destination.y
        theta_m = math.atan2(delta_my,delta_mx)
        
        abscisse_curv = rayon * abs(theta_m - theta_r)
        
        #calcul de durée totale
        self.set_vitesse_translation("arc_de_cercle")
        self.avancer(abscisse_curv)
        
        #nouvelle position
        self.x =    0 + rayon*math.cos(theta_m)
        self.y = 2000 + rayon*math.sin(theta_m)
        
        
    def set_vitesse_translation(self, vitesse):
        """
        Spécifie une vitesse de translation en metres par seconde, suivant les conventions choisies dans l'interface.
        """
        pwm_max = RobotInterface.conventions_vitesse_translation(vitesse)
        vitesse_mmps = 2500/(613.52 * pwm_max**(-1.034))
        self.vitesse_translation = vitesse_mmps
    
    def set_vitesse_rotation(self, vitesse, rayon=None):
        """
        Spécifie une vitesse de rotation en radians par seconde, suivant les conventions choisies dans l'interface.
        """
        pwm_max = RobotInterface.conventions_vitesse_rotation(vitesse,rayon)
        vitesse_rps = math.pi/(277.85 * pwm_max**(-1.222))
        self.vitesse_rotation = vitesse_rps
        
    def actionneurs_bougie(self, en_haut, angle):
        pass
    
    def actionneur_cadeau(self, angle):
        pass
            
    def gonflage_ballon(self):
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

