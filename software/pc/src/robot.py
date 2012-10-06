from time import time
from mutex import Mutex

class Robot:
    def __init__(self,deplacements,config,log):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.deplacements = deplacements
        self.config = config
        self.log = log
        
        """
        attributs des coordonnées du robot.
        sont mis à jour automatiquement par un thread dédié communiquant via la série.
        dans le code, on peut utiliser directement :
        self.x, self.y, self.orientation : coordonnées courantes
        self.blocage : booléen True si le robot est considéré comme bloqué hors de la consigne
        self.enMouvement : booléen True si le robot est encore en mouvement
        les écritures et lectures sur ces attributs passent par des mutex gérant les accès mémoire, et communiquent avec la série si nécessaire
        """
        self._x = 0
        self._y = 0
        self._orientation = 0
        self._blocage = False
        self._enCoursDeBlocage = False
        self._enMouvement = False
        
        #durée de jeu TODO : à muter dans Table ?
        self.debut_jeu = time()
        
        
    #####################################################################################
    ### ACCESSEURS SUR LES ATTRIBUTS DU ROBOT , MÉTHODES DE MISES À JOUR AUTOMATIQUES ###
    #####################################################################################
    
    def __setattr__(self, attribut, value):
        setters = {
            "x":self.set_x,
            "y":self.set_y,
            "orientation":self.set_orientation,
            "blocage":self.set_blocage,
            "enMouvement":self.set_enMouvement
        }
        if attribut in setters:
            setters[attribut](value)
        else:
            self.__dict__[attribut] = value
            
    def __getattr__(self, attribut):
        getters = {
            "x":self.get_x,
            "y":self.get_y,
            "orientation":self.get_orientation,
            "blocage":self.get_blocage,
            "enMouvement":self.get_enMouvement
        }
        if attribut in getters:
            return getters[attribut]()
            
    def get_x(self):
        with self.mutex:
            return self.__dict__["_x"]
            
    def set_x(self, value):
        self.deplacements.set_x(value)
        
    def get_y(self):
        with self.mutex:
            return self.__dict__["_y"]
    
    def set_y(self, value):
        self.deplacements.set_y(value)
     
    def get_orientation(self):
        with self.mutex:
            return self.__dict__["_orientation"]
       
    def set_orientation(self, value):
        self.deplacements.set_orientation(value)
        
    def get_enMouvement(self):
        with self.mutex:
            return self.__dict__["_enMouvement"]
        
    def set_enMouvement(self, value):
        with self.mutex:
            self.__dict__["_enMouvement"] = value
            
    def get_blocage(self):
        with self.mutex:
            return self.__dict__["_blocage"]
            
    def set_blocage(self, value):
        with self.mutex:
            self.__dict__["_blocage"] = value
            
    def update_enMouvement(self, erreur_rotation, erreur_translation, derivee_erreur_rotation, derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        """
        rotation_stoppe = erreur_rotation < 105
        translation_stoppe = erreur_translation < 100
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        
        self.enMouvement = not(rotation_stoppe and translation_stoppe and bouge_pas)
    
    def gestion_blocage(self,PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation, **useless):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection automatique des collisions, qui stoppe le robot lorsqu'il patine
        """
        moteur_force = PWMmoteurGauche > 45 or PWMmoteurDroit > 45
        bouge_pas = derivee_erreur_rotation==0 and derivee_erreur_translation==0
            
        if (bouge_pas and moteur_force):
            if self._enCoursDeBlocage:
                #la durée de tolérance au patinage est fixée ici 
                if time() - self.debut_timer_blocage > 0.5:
                    self.log.warning("le robot a dû s'arrêter suite à un patinage.")
                    self.deplacements.stopper()
                    self.blocage = True
            else:
                self.debut_timer_blocage = time()
                self._enCoursDeBlocage = True
        else:
            self._enCoursDeBlocage = False
            
    def update_x_y_orientation(self, x, y, orientation_milliRadians):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de mise à jour des coordonnées du robot
        """
        with self.mutex:
            self.__dict__["_x"] = x
            self.__dict__["_y"] = y
            self.__dict__["_orientation"] = orientation_milliRadians/1000.
            
            
            
    #####################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE BASE , AVEC GESTION DES ACQUITTEMENTS ET CAPTEURS ###
    #####################################################################################
    
    def avancer(self, distance):
        #le robot n'est plus considéré comme bloqué
        self.blocage = False
        #utilisation du service de déplacement
        self.deplacements.avancer(distance)
        #TODO boucle d'acquittement
        
        
    ##################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE HAUT NIVEAU , AVEC RELANCES EN CAS DE PROBLÈME ###
    ##################################################################################
    
    def gestion_avancer(self, distance):
        retour = self.avancer(distance)
        if retour == "capteur":
            self.stopper()
        #etc..
        