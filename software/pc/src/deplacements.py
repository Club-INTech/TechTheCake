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
            "derivee_erreur_translation" : 0
            }   

    def gestion_blocage(self,PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection automatique des collisions, qui stoppe le robot lorsqu'il patine
        retourne True si la valeur du booléen blocage (attribut de robot) doit etre remplacée par True
        """
        blocage = False
        
        moteur_force = abs(PWMmoteurGauche) > 40 or abs(PWMmoteurDroit) > 40
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
        
    def update_enMouvement(self, erreur_rotation, erreur_translation, derivee_erreur_rotation, derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        retourne la valeur du booléen enMouvement (attribut de robot)
        """
        rotation_stoppe = abs(erreur_rotation) < 105
        translation_stoppe = abs(erreur_translation) < 100
        #bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        bouge_pas = abs(derivee_erreur_rotation) < 100 and abs(derivee_erreur_translation) < 100
        
        return not(rotation_stoppe and translation_stoppe and bouge_pas)
        
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
        
    def set_vitesse_translation(self, pwm_max):
        """
        modifie la vitesse de translation (pwm_max) du robot et adapte les constantes d'asservissement
        """
          
        # les constantes d'asservissement sont valables dans des plages de vitesses
        if pwm_max > 120:
            kp = 0.8
            kd = 22.0
        elif pwm_max > 55:
            kp = 0.8
            kd = 16.0
        else:
            kp = 0.6
            kd = 10.0
        
        #envoi des nouvelles constantes à la couche d'asservissement
        envoi = ["ctv"]
        envoi.append(float(kp))
        envoi.append(float(kd))
        envoi.append(int(pwm_max))
        
        self.serie.communiquer("asservissement",envoi, 0)
        
    def set_vitesse_rotation(self, pwm_max):
        """
        modifie la vitesse de rotation (pwm_max) du robot et adapte les constantes d'asservissement
        """
          
        # les constantes d'asservissement sont valables dans des plages de vitesses
        if pwm_max > 155:
            kp = 1.0
            kd = 23.0
        elif pwm_max > 90:
            kp = 1.0
            kd = 19.0
        else:
            kp = 0.8
            kd = 15.0
        
        #envoi des nouvelles constantes à la couche d'asservissement
        envoi = ["crv"]
        envoi.append(float(kp))
        envoi.append(float(kd))
        envoi.append(int(pwm_max))
        
        self.serie.communiquer("asservissement",envoi, 0)
        
    def get_infos_stoppage_enMouvement(self):
        infos_string = self.serie.communiquer("asservissement","?infos",4)
        infos_int = list(map(lambda x: int(x), infos_string))
        
        deriv_erreur_rot = infos_int[2] - self.infos_stoppage_enMouvement["erreur_rotation"]
        deriv_erreur_tra = infos_int[3] - self.infos_stoppage_enMouvement["erreur_translation"]
        
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : infos_int[0],
            "PWMmoteurDroit" : infos_int[1],
            "erreur_rotation" : infos_int[2],
            "erreur_translation" : infos_int[3],
            "derivee_erreur_rotation" : deriv_erreur_rot,
            "derivee_erreur_translation" : deriv_erreur_tra
            }
            
        return self.infos_stoppage_enMouvement
    
    def get_infos_x_y_orientation(self):
        infos_string = self.serie.communiquer("asservissement","?xyo",3)
        return list(map(lambda x: int(x), infos_string))
        
    def arret_final(self):
        self.serie.set_arret_serie()