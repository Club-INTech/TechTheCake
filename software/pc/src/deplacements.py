#module natif pour les méthodes abstraites
import abc
#client SOAP pour le simulateur
from suds.client import Client

import os
from time import sleep

from mutex import Mutex

################################################
## CLASSE D'INTERFACE POUR LES DEPLACEMENTS  ###
################################################
class Deplacements(metaclass=abc.ABCMeta):
    """
    classe d'interface pour les déplacements
    les méthodes abstraites définies ici doivent impérativement être surchargées dans les classes filles
    (DeplacementsSimulateur et DeplacementsSerie)
    """
    
    @abc.abstractmethod
    def gestion_blocage(self, **params):
        pass
    
    @abc.abstractmethod
    def update_enMouvement(self, **params):
        pass
    
    @abc.abstractmethod
    def avancer(self, distance):
        pass
    
    @abc.abstractmethod
    def tourner(self, angle):
        pass
    
    @abc.abstractmethod
    def set_x(self, new_x):
        pass
    
    @abc.abstractmethod
    def set_y(self, new_y):
        pass
    
    @abc.abstractmethod
    def set_orientation(self, new_o):
        pass
    
    @abc.abstractmethod
    def activer_asservissement_translation(self):
        pass
        
    @abc.abstractmethod
    def activer_asservissement_rotation(self):
        pass
        
    @abc.abstractmethod
    def desactiver_asservissement_translation(self):
        pass
        
    @abc.abstractmethod
    def desactiver_asservissement_rotation(self):
        pass
    
    @abc.abstractmethod
    def stopper(self):
        pass
    
    @abc.abstractmethod
    def set_vitesse_translation(self, valeur):
        pass
    
    @abc.abstractmethod
    def set_vitesse_rotation(self, valeur):
        pass
    
    @abc.abstractmethod
    def get_infos_stoppage_enMouvement(self):
        pass
    
    @abc.abstractmethod
    def get_infos_x_y_orientation(self):
        pass
    

##############################################################
## CLASSE POUR LES DEPLACEMENTS RÉELS (ENVOI SUR LA SÉRIE) ###
##############################################################
class DeplacementsSerie(Deplacements):
    """
    classe gérant les envoi sur la série de la carte d'asservissement.
    hérite de la classe d'interface Deplacements
    """
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        self._enCoursDeBlocage
        
        #sauvegarde d'infos bas niveau sur l'état du robot, réutilisées par plusieurs calculs dans le thread de mise à jour
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : 0,
            "PWMmoteurDroit" : 0,
            "erreur_rotation" : 0,
            "erreur_translation" : 0,
            "derivee_erreur_rotation" : 0,
            "derivee_erreur_translation" : 0
            }   

    def update_enMouvement(self, erreur_rotation, erreur_translation, derivee_erreur_rotation, derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        retourne la valeur du booléen enMouvement (attribut de robot)
        """
        rotation_stoppe = erreur_rotation < 105
        translation_stoppe = erreur_translation < 100
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        
        return not(rotation_stoppe and translation_stoppe and bouge_pas)
    
    def gestion_blocage(self,PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection automatique des collisions, qui stoppe le robot lorsqu'il patine
        retourne True si la valeur du booléen blocage (attribut de robot) doit etre remplacée par True
        """
        blocage = False
        
        moteur_force = PWMmoteurGauche > 45 or PWMmoteurDroit > 45
        bouge_pas = derivee_erreur_rotation==0 and derivee_erreur_translation==0
            
        if (bouge_pas and moteur_force):
            if self._enCoursDeBlocage:
                #la durée de tolérance au patinage est fixée ici 
                if time() - self.debut_timer_blocage > 0.5:
                    self.log.warning("le robot a dû s'arrêter suite à un patinage.")
                    self.stopper()
                    blocage = True
            else:
                self.debut_timer_blocage = time()
                self._enCoursDeBlocage = True
        else:
            self._enCoursDeBlocage = False
        return blocage
            
            
    def avancer(self, distance):
        """
        fait avancer le robot en ligne droite. (distance<0 => reculer)
        """
        self.serie.communiquer("asservissement",["d",float(distance)], 0)
    
       
    def tourner(self, angle):
        """
        oriente le robot à un angle dans le repère de la table.
        """
        self.serie.communiquer("asservissement",["t",float(angle)], 0)
        
    def set_x(self, new_x):
        """
        écrase la position sur x du robot.
        """
        self.serie.communiquer("asservissement",["cx",float(new_x)], 0)
        
    def set_y(self, new_y):
        """
        écrase la position sur y du robot.
        """
        self.serie.communiquer("asservissement",["cy",float(new_y)], 0)
        
    def set_orientation(self, new_o):
        """
        écrase l'orientation du robot.
        """
        self.serie.communiquer("asservissement",["co",float(new_o)], 0)
        
    def activer_asservissement_translation(self):
        self.serie.communiquer("asservissement","ct1", 0)
        
    def activer_asservissement_rotation(self):
        self.serie.communiquer("asservissement","cr1", 0)
        
    def desactiver_asservissement_translation(self):
        self.serie.communiquer("asservissement","ct0", 0)
        
    def desactiver_asservissement_rotation(self):
        self.serie.communiquer("asservissement","cr0", 0)
        
        ##########################
        
    def stopper(self):
        """
        stoppe le robot (l'asservit sur place)
        """
        self.serie.communiquer("asservissement","stop", 0)
        
    def set_vitesse_translation(self, valeur):
        """
        spécifie une vitesse prédéfinie en translation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        #definition des constantes d'asservissement en fonction de la vitesse
        kp_translation = [0.75,0.75,0.5]
        kd_translation = [2.0,2.5,4.0]
        vb_translation = [60,100,200]
        
        envoi = ["ctv"]
        envoi.append(float(kp_translation[valeur-1]))
        envoi.append(float(kd_translation[valeur-1]))
        envoi.append(int(vb_translation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
        
    def set_vitesse_rotation(self, valeur):
        """
        spécifie une vitesse prédéfinie en rotation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        #definition des constantes d'asservissement en fonction de la vitesse
        kp_rotation = [1.5,1.2,0.9]
        kd_rotation = [2.0,3.5,3.5]
        vb_rotation = [80,100,200]
        
        envoi = ["crv"]
        envoi.append(float(kp_rotation[valeur-1]))
        envoi.append(float(kd_rotation[valeur-1]))
        envoi.append(int(vb_rotation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
            
    def get_infos_stoppage_enMouvement(self):
        infos_string = self.serie.communiquer("asservissement","?infos",4)
        infos_string = list(map(lambda x: int(x), infos_string))
        
        deriv_erreur_rot = infos_string[2] - self.infos_stoppage_enMouvement["erreur_rotation"]
        deriv_erreur_tra = infos_string[3] - self.infos_stoppage_enMouvement["erreur_translation"]
        
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : infos_string[0],
            "PWMmoteurDroit" : infos_string[1],
            "erreur_rotation" : infos_string[2],
            "erreur_translation" : infos_string[3],
            "derivee_erreur_rotation" : deriv_erreur_rot,
            "derivee_erreur_translation" : deriv_erreur_tra
            }
            
        return self.infos_stoppage_enMouvement
    
    def get_infos_x_y_orientation(self):
        infos_string = self.serie.communiquer("asservissement","?xyo",3)
        return list(map(lambda x: int(x), infos_string))
        
        
#################################################
## CLASSE POUR LES DEPLACEMENTS EN SIMULATION ###
#################################################
class DeplacementsSimulateur(Deplacements):
    """
    classe gérant la simulation des déplacements du robot
    hérite de la classe d'interface Deplacements
    """
    def __init__(self,simulateur,config,log):
             
        self.simulateur = simulateur
        self.config=config
        self.log=log
        
    def gestion_blocage(self, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection des collisions
        retourne True si la valeur du booléen blocage (attribut de robot) doit etre remplacée par True
        """
        return self.simulateur.gestion_blocage()
    
    def update_enMouvement(self, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode détermine si le robot est arrivé à sa position de consigne
        retourne la valeur du booléen enMouvement (attribut de robot)
        """
        return self.simulateur.update_enMouvement()
    
    def get_infos_stoppage_enMouvement(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        """
        return self.simulateur.get_infos_stoppage_enMouvement()
        
    def est_bloque(self):
        return self.simulateur.est_bloque()
        
    def est_arrive(self):
        return self.simulateur.est_arrive()
    
    def get_infos_x_y_orientation(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        """
        return self.simulateur.get_infos_x_y_orientation()
      
            
    def avancer(self, distance):
        self.simulateur.avancer(distance)

    def tourner(self, angle):
        self.simulateur.tourner(angle)
    
    def set_x(self, new_x):
        pass
    
    def set_y(self, new_y):
        pass
    def set_orientation(self, new_o):
        pass

    def activer_asservissement_translation(self):
        pass
        
    def activer_asservissement_rotation(self):
        pass
        
    def desactiver_asservissement_translation(self):
        pass
        
    def desactiver_asservissement_rotation(self):
        pass
    
    def stopper(self):
        self.simulateur.stopper() 
    
    def set_vitesse_translation(self, valeur):
        pass
    
    def set_vitesse_rotation(self, valeur):
        pass
