from time import time

class Deplacements():
    """
    classe gérant les envoi sur la série de la carte d'asservissement.
    hérite de la classe d'interface Deplacements
    """
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        self._enCoursDeBlocage = False
        
        #sauvegarde d'infos bas niveau sur l'état du robot, réutilisées par plusieurs calculs dans le thread de mise à jour
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : 0,
            "PWMmoteurDroit" : 0,
            "erreur_rotation" : 0,
            "erreur_translation" : 0,
            "derivee_erreur_rotation" : 0,
            "derivee_erreur_translation" : 0,
            "derivee2_erreur_rotation" : 0,
            "derivee2_erreur_translation" : 0
            }   

    def gestion_blocage(self,PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection automatique des collisions, qui stoppe le robot lorsqu'il patine
        retourne True si la valeur du booléen blocage (attribut de robot) doit etre remplacée par True
        """
        blocage = False
        
        moteur_force = abs(PWMmoteurGauche) > 45 or abs(PWMmoteurDroit) > 45
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
        
    def update_enMouvement(self, derivee_erreur_rotation, derivee_erreur_translation, derivee2_erreur_rotation, derivee2_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        retourne la valeur du booléen enMouvement (attribut de robot)
        """
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        bouge_pas_du_tout = derivee2_erreur_rotation == 0 and derivee2_erreur_translation == 0
        
        return not(bouge_pas and bouge_pas_du_tout)
        
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
    
    def stopper(self):
        """
        stoppe le robot (l'asservit sur place)
        """
        self.serie.communiquer("asservissement","stop", 0)
        
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
        
    def set_vitesse_translation(self, valeur):
        """
        spécifie une vitesse prédéfinie en translation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        envoi = ["ctv"]
        if valeur < 5:
            #definition des constantes d'asservissement en fonction de la vitesse
            kp_translation = [0.75,0.75,0.5]
            kd_translation = [2.0,2.5,4.0]
            vb_translation = [40,100,200]
            
            envoi.append(float(kp_translation[valeur-1]))
            envoi.append(float(kd_translation[valeur-1]))
            envoi.append(int(vb_translation[valeur-1]))
        else:
            envoi.append(0.25)
            envoi.append(9.0)
            envoi.append(int(valeur))
        self.serie.communiquer("asservissement",envoi, 0)
        
    def set_vitesse_rotation(self, valeur):
        """
        spécifie une vitesse prédéfinie en rotation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        envoi = ["crv"]
        if valeur < 5:
            #definition des constantes d'asservissement en fonction de la vitesse
            kp_rotation = [0.25,1.2,0.9]
            kd_rotation = [2.0,3.5,3.5]
            vb_rotation = [60,100,200]
        
            envoi.append(float(kp_rotation[valeur-1]))
            envoi.append(float(kd_rotation[valeur-1]))
            envoi.append(int(vb_rotation[valeur-1]))
        else:
            envoi.append(0.8)
            envoi.append(15.0)
            envoi.append(int(valeur))
        self.serie.communiquer("asservissement",envoi, 0)
        
    def get_infos_stoppage_enMouvement(self):
        infos_string = self.serie.communiquer("asservissement","?infos",4)
        infos_int = list(map(lambda x: int(x), infos_string))
        
        deriv_erreur_rot = infos_int[2] - self.infos_stoppage_enMouvement["erreur_rotation"]
        deriv_erreur_tra = infos_int[3] - self.infos_stoppage_enMouvement["erreur_translation"]
        
        deriv2_erreur_rot = deriv_erreur_rot - self.infos_stoppage_enMouvement["derivee_erreur_rotation"] 
        deriv2_erreur_tra = deriv_erreur_tra - self.infos_stoppage_enMouvement["derivee_erreur_translation"]
        
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : infos_int[0],
            "PWMmoteurDroit" : infos_int[1],
            "erreur_rotation" : infos_int[2],
            "erreur_translation" : infos_int[3],
            "derivee_erreur_rotation" : deriv_erreur_rot,
            "derivee_erreur_translation" : deriv_erreur_tra,
            "derivee2_erreur_rotation" : deriv2_erreur_rot,
            "derivee2_erreur_translation" : deriv2_erreur_tra
            }
            
        return self.infos_stoppage_enMouvement
    
    def get_infos_x_y_orientation(self):
        infos_string = self.serie.communiquer("asservissement","?xyo",3)
        return list(map(lambda x: int(x), infos_string))
        
    def arret_final(self):
        self.serie.set_arret_serie()