# -*- coding: utf-8 -*-

import serie
import attributions
import time

class Asservissement():
    """
    Classe 
    """
    def __init__(self):
        chemins = attributions.attribuer()
        cheminAsser = chemins[0]
        self.serieAsserInstance = serie.Serie(cheminAsser, 9600, 3)
        
        self.est_bloque = False
        self.est_stoppe = False
        self.debut_timer_blocage = time.time()

    def gestion_stoppage(self):
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
            
    def robot_arret(self):
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
        if self.robot_arret():
            if self.est_stoppe:
                return "robot à l'arrêt"
            else:
                return "robot arrivé"
        else:
            return "robot en mouvement"