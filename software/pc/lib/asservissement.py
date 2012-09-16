# -*- coding: utf-8 -*-

import serie
import attributions
import time
from threading import Lock

class Asservissement():
    """
    Classe 
    """
    def __init__(self):
        chemins = attributions.attribuer()
        cheminAsser = chemins[0]
        self.serieAsserInstance = serie.Serie(cheminAsser, 9600, 3)
        
        self.mutex_serie_asservissement = Lock()
        
        self.est_bloque = False
        self.est_stoppe = False
        self.debut_timer_blocage = time.time()
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2

    def gestion_stoppage(self):
        self.mutex_serie_asservissement.acquire()
        self.serieAsserInstance.ecrire("?bloc")
        PWMmoteurGauche = int(self.serieAsserInstance.lire())
        PWMmoteurDroit = int(self.serieAsserInstance.lire())
        derivee_erreur_rotation = int(self.serieAsserInstance.lire())
        derivee_erreur_translation = int(self.serieAsserInstance.lire())
        
        moteur_force = PWMmoteurGauche > 45 or PWMmoteurDroit > 45
        bouge_pas = derivee_erreur_rotation==0 and derivee_erreur_translation==0
            
        if (bouge_pas and moteur_force):
            if self.est_bloque:
                if time.time() - self.debut_timer_blocage > 0.5:
                    self.serieAsserInstance.ecrire("stop")
                    self.est_stoppe = True
            else:
                self.debut_timer_blocage = time.time()
                self.est_bloque = True
        else:
            self.est_bloque = False
        self.mutex_serie_asservissement.release()
            
    def robot_est_arrete(self):
        self.mutex_serie_asservissement.acquire()
        self.serieAsserInstance.ecrire("?arret")
        erreur_rotation = int(self.serieAsserInstance.lire())
        erreur_translation = int(self.serieAsserInstance.lire())
        derivee_erreur_rotation = int(self.serieAsserInstance.lire())
        derivee_erreur_translation = int(self.serieAsserInstance.lire())
        self.mutex_serie_asservissement.release()
        
        rotation_stoppe = erreur_rotation < 105
        translation_stoppe = erreur_translation < 100
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        
        return rotation_stoppe and translation_stoppe and bouge_pas

    def acquittement(self):
        if self.robot_est_arrete():
            if self.est_stoppe:
                return "robot à l'arrêt"
            else:
                return "robot arrivé"
        else:
            return "robot en mouvement"
            
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
        
        self.mutex_serie_asservissement.acquire()
        self.serieAsserInstance.ecrire("ctv")
        self.serieAsserInstance.ecrire(float(kp_translation[valeur-1]))
        self.serieAsserInstance.ecrire(float(kd_translation[valeur-1]))
        self.serieAsserInstance.ecrire(int(vb_translation[valeur-1]))
        self.mutex_serie_asservissement.release()
        
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
        kp_rotation = [0.75,0.75,0.5]
        kd_rotation = [2.0,2.5,4.0]
        vb_rotation = [60,100,200]
        
        self.mutex_serie_asservissement.acquire()
        self.serieAsserInstance.ecrire("crv")
        self.serieAsserInstance.ecrire(float(kp_rotation[valeur-1]))
        self.serieAsserInstance.ecrire(float(kd_rotation[valeur-1]))
        self.serieAsserInstance.ecrire(int(vb_rotation[valeur-1]))
        self.mutex_serie_asservissement.release()
        
        #sauvegarde de la valeur choisie
        self.vitesse_rotation = int(valeur)
        
    def avancer(self, distance):
        """
        Fonction de script pour faire avancer le robot en ligne droite. (distance <0 => reculer)c
        :param distance: Distance à parcourir
        :type angle: Float
        """
        
        self.mutex_serie_asservissement.acquire()
        self.serieAsserInstance.ecrire("d")
        self.serieAsserInstance.ecrire(float(distance))
        self.mutex_serie_asservissement.release()