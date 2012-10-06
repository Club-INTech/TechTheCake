import abc

class Deplacements(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def parle(self):
        pass
    
    #changer_vitesse_translation
    #changer_vitesse_rotation
    #avancer
    #tourner
    #get_x
    #get_y
    #get_orientation
    #stopper
    #get_infos_stoppage
    #get_infos_enMouvement
    
    
class DeplacementsSerie:
    """
    classe gérant les envoi sur la série de la carte d'asservissement.
    hérite de la classe SerialManager
    """
    def __init__(self,serie,config,log):
        self.serie = serie
        self.config = config
        self.log = log
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #sauvegarde d'infos bas niveau sur l'état du robot, réutilisées par plusieurs calculs dans le thread de mise à jour
        self.infos_stoppage_enMouvement={
            "PWMmoteurGauche" : 0,
            "PWMmoteurDroit" : 0,
            "erreur_rotation" : 0,
            "erreur_translation" : 0,
            "derivee_erreur_rotation" : 0,
            "derivee_erreur_translation" : 0
            }

    def parle(self):
        print("déplacements pour la série")
    
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
        
        envoi = ["ctv"]
        envoi.append(float(kp_translation[valeur-1]))
        envoi.append(float(kd_translation[valeur-1]))
        envoi.append(int(vb_translation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
        
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
        
        envoi = ["crv"]
        envoi.append(float(kp_rotation[valeur-1]))
        envoi.append(float(kd_rotation[valeur-1]))
        envoi.append(int(vb_rotation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
            
        #sauvegarde de la valeur choisie
        self.vitesse_rotation = int(valeur)
        
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
        
    def avancer(self, distance):
        """
        Fonction de script pour faire avancer le robot en ligne droite. (distance<0 => reculer)
        """
        self.serie.communiquer("asservissement",["d",float(distance)], 0)
        
    def stopper(self):
        """
        Fonction de script pour stopper le robot (l'asservir sur place)
        """
        self.serie.communiquer("asservissement","stop", 0)

        
class DeplacementsSimulateur(Deplacements):

    def __init__(self,config,log):
        self.config = config
        self.log = log
        
    def parle(self):
        print("déplacements pour la simulation")