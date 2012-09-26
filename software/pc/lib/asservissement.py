# -*- coding: utf-8 -*-

import serie
import attributions
import time
from threading import Lock

class Mutex():
    """
    Classe de mutex permettant de factoriser leur utilisation dans des blocs with
    """
    self.mutex_serie_asservissement = Lock()
        
    def __enter__(self):
        self.mutex_serie_asservissement.acquire()
    
    def __exit__(self, type, value, tb):
        self.mutex_serie_asservissement.release()
    
class Asservissement():
    """
    Classe 
    """
    def __init__(self):
        chemins = attributions.attribuer()
        cheminAsser = chemins[0]
        self.serieAsserInstance = serie.Serie(cheminAsser, 9600, 3)
        
        self.mutex = Mutex()
        
        self.est_bloque = False
        self.est_stoppe = False
        self.debut_timer_blocage = time.time()
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2

    def gestion_stoppage(self):
        """
        méthode de détection automatique des collisions, qui stoppe le robot lorsqu'il patine
        """
        with self.mutex:
            self.serieAsserInstance.ecrire("?bloc")
            PWMmoteurGauche = int(self.serieAsserInstance.lire())
            PWMmoteurDroit = int(self.serieAsserInstance.lire())
            derivee_erreur_rotation = int(self.serieAsserInstance.lire())
            derivee_erreur_translation = int(self.serieAsserInstance.lire())
            
            moteur_force = PWMmoteurGauche > 45 or PWMmoteurDroit > 45
            bouge_pas = derivee_erreur_rotation==0 and derivee_erreur_translation==0
                
            if (bouge_pas and moteur_force):
                if self.est_bloque:
                    #la durée de tolérance au patinage est fixée ici 
                    if time.time() - self.debut_timer_blocage > 0.5:
                        self.serieAsserInstance.ecrire("stop")
                        self.est_stoppe = True
                else:
                    self.debut_timer_blocage = time.time()
                    self.est_bloque = True
            else:
                self.est_bloque = False
            
    def robot_est_arrete(self):
        """
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        """
        with self.mutex:
            self.serieAsserInstance.ecrire("?arret")
            erreur_rotation = int(self.serieAsserInstance.lire())
            erreur_translation = int(self.serieAsserInstance.lire())
            derivee_erreur_rotation = int(self.serieAsserInstance.lire())
            derivee_erreur_translation = int(self.serieAsserInstance.lire())
        
        rotation_stoppe = erreur_rotation < 105
        translation_stoppe = erreur_translation < 100
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        
        return rotation_stoppe and translation_stoppe and bouge_pas

    def acquittement(self):
        """
        méthode renvoyant l'état de l'acquittement du robot
        en mouvement (position != consigne), arrivé à la consigne (de la stratégie), ou arreté par un obstacle (consigne forcée)
        la convention sur les return est à déterminer
        """
        if self.robot_est_arrete():
            if self.est_stoppe:
                return "robot à l'arrêt"
            else:
                return "robot arrivé"
        else:
            return "robot en mouvement"
           
            
            
            
            
            
            
            
            
            
            
    ###########################################################################################
    ##FONCTIONS DE DEPLACEMENTS ( != de l'asservissement. à migrer vers une autre classe ?) ###
    ###########################################################################################
            
    def changer_vitesse_translation(self, valeur):
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
        
        with self.mutex:
            self.serieAsserInstance.ecrire("ctv")
            self.serieAsserInstance.ecrire(float(kp_translation[valeur-1]))
            self.serieAsserInstance.ecrire(float(kd_translation[valeur-1]))
            self.serieAsserInstance.ecrire(int(vb_translation[valeur-1]))
        
        #sauvegarde de la valeur choisie
        self.vitesse_translation = int(valeur)
        
    def changer_vitesse_rotation(self, valeur):
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
        
        with self.mutex:
            self.serieAsserInstance.ecrire("crv")
            self.serieAsserInstance.ecrire(float(kp_rotation[valeur-1]))
            self.serieAsserInstance.ecrire(float(kd_rotation[valeur-1]))
            self.serieAsserInstance.ecrire(int(vb_rotation[valeur-1]))
        
        #sauvegarde de la valeur choisie
        self.vitesse_rotation = int(valeur)
        
    def avancer(self, distance):
        """
        Fonction de script pour faire avancer le robot en ligne droite. (distance <0 => reculer)
        :param distance: Distance à parcourir
        :type angle: Float
        """
        with self.mutex:
            self.serieAsserInstance.ecrire("d")
            self.serieAsserInstance.ecrire(float(distance))
        
        #pour redémarrer la gestion_stoppage : le robot n'est plus considéré à l'arret
        self.est_stoppe = False
        
        