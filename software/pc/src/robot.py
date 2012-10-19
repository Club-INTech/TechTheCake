import math
from time import time,sleep
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
        self._enMouvement = True
        
        #sauvegarde des vitesses courantes du robot
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #durée de jeu TODO : à muter dans Table ?
        self.debut_jeu = time()
        
        #couleur du robot
        self.couleur = "bleu"
        
        
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
        getters = [
            "x",
            "y",
            "orientation",
            "blocage",
            "enMouvement"
        ]
        if attribut in getters:
            with self.mutex:
                return self.__dict__["_"+attribut]
        
    def set_x(self, value):
        self.deplacements.set_x(value)
        
    def set_y(self, value):
        self.deplacements.set_y(value)
     
    def set_orientation(self, value):
        self.deplacements.set_orientation(value)
        
    def set_enMouvement(self, value):
        with self.mutex:
            self.__dict__["_enMouvement"] = value
            
    def set_blocage(self, value):
        with self.mutex:
            self.__dict__["_blocage"] = value
            
    def update_x_y_orientation(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de mise à jour des coordonnées du robot
        """
        [x,y,orientation_milliRadians] = self.deplacements.get_infos_x_y_orientation()
        with self.mutex:
            self.__dict__["_x"] = x
            self.__dict__["_y"] = y
            self.__dict__["_orientation"] = orientation_milliRadians/1000.
            
            
    #####################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE BASE , AVEC GESTION DES ACQUITTEMENTS ET CAPTEURS ###
    #####################################################################################
    
    def avancer(self, distance):
        self.deplacements.avancer(distance)
        self._boucle_acquittement()
        
    def tourner(self, angle):
        self.deplacements.tourner(angle)
        self._boucle_acquittement()
        
    # Utiliser des exceptions en cas d'arrêt anormal (blocage, capteur etc...)
    def _boucle_acquittement(self):
        while 1:
            #robot bloqué ?
            if self.deplacements.est_bloque():
                self.deplacements.stopper()
                print("abandon car blocage")
                break
            #robot arrivé ?
            if self.deplacements.est_arrive():
                print("robot arrivé")
                break
            sleep(0.5)
        pass
    
    def recaler(self):
        
        #TODO utiliser table
        LONGUEUR_TABLE = 3000
        LARGEUR_ROBOT = 400
        #
        
        self.set_vitesse_translation(1)
        self.set_vitesse_rotation(1)
        self.avancer(-1000)
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        # self.avancer(-300)
        if self.couleur == "bleu":
            self.x = -LONGUEUR_TABLE/2. + LARGEUR_ROBOT/1.999
            self.orientation = 0.0
        else:
            self.x = LONGUEUR_TABLE/2. - LARGEUR_ROBOT/1.999
            self.orientation = math.pi
        self.deplacements.activer_asservissement_rotation()
        #sleep(0.5)
        self.set_vitesse_translation(1)
        self.avancer(100)
        self.tourner(math.pi/2)
        self.avancer(-1000)
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300)
        self.y = LARGEUR_ROBOT/1.999
        self.orientation = math.pi/2.
        self.deplacements.activer_asservissement_rotation()
        # sleep(0.5)
        self.set_vitesse_translation(1)
        self.avancer(150)
        if self.couleur == "bleu":
            self.tourner(0.0)
        else:
            self.tourner(math.pi)
        self.set_vitesse_translation(2)
        self.set_vitesse_rotation(2)
        
        
    #############################################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE HAUT NIVEAU (TROUVÉES DANS LES SCRIPTS), AVEC RELANCES EN CAS DE PROBLÈME ###
    #############################################################################################################
    
    def gestion_avancer(self, distance):
        retour = self.avancer(distance)
        if retour == "capteur":
            self.stopper()
        #etc..
        
    def gestion_tourner(self, angle):
        retour = self.tourner(angle)
        if retour == "capteur":
            self.stopper()
        #etc..
        
    def set_vitesse_translation(self, valeur):
        self.deplacements.set_vitesse_translation(valeur)
        self.vitesse_translation = int(valeur)
    
    def set_vitesse_rotation(self, valeur):
        self.deplacements.set_vitesse_rotation(valeur)
        self.vitesse_rotation = int(valeur)
