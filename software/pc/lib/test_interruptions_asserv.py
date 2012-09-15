# -*- coding: utf-8 -*-

import serie
import attributions
import time

chemins = attributions.attribuer()
cheminAsser = chemins[0]
serieAsserInstance = serie.Serie(cheminAsser, 9600, 3)

def gestion_stoppage():
    global est_bloque
    global est_stoppe
    global debut_timer
    serieAsserInstance.ecrire("?bloc")
    PWMmoteurGauche = int(serieAsserInstance.lire())
    PWMmoteurDroit = int(serieAsserInstance.lire())
    derivee_erreur_rotation = int(serieAsserInstance.lire())
    derivee_erreur_translation = int(serieAsserInstance.lire())
    
    moteur_force = PWMmoteurGauche > 45 or PWMmoteurDroit > 45
    bouge_pas = derivee_erreur_rotation==0 and derivee_erreur_translation==0
        
    if (bouge_pas and moteur_force):
        if est_bloque:
            if time.time() - debut_timer > 0.5:
                serieAsserInstance.ecrire("stop")
                est_stoppe = True
        else:
            debut_timer = time.time()
            est_bloque = True
    else:
        est_bloque = False
        
def robot_arret():
    serieAsserInstance.ecrire("?arret")
    erreur_rotation = int(serieAsserInstance.lire())
    erreur_translation = int(serieAsserInstance.lire())
    derivee_erreur_rotation = int(serieAsserInstance.lire())
    derivee_erreur_translation = int(serieAsserInstance.lire())
    
    rotation_stoppe = erreur_rotation < 105
    translation_stoppe = erreur_translation < 100
    bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
    
    return rotation_stoppe and translation_stoppe and bouge_pas

def acquittement():
    if robot_arret():
        if est_stoppe:
            return "robot à l'arrêt"
        else:
            return "robot arrivé"
    else:
        return "robot en mouvement"
    
est_bloque = False
est_stoppe = False
debut_timer = time.time()

while 42:
    gestion_stoppage()
    print acquittement()
    print "####"