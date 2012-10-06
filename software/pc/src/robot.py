from time import time
from mutex import Mutex

class Robot:
    def __init__(self,deplacements,config,log):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.deplacements = deplacements
        self.config = config
        self.log = log
        
        #attributs "physiques"
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.debut_jeu = time()
        
        self.blocage = False
        self._enCoursDeBlocage = False
        self.enMouvement = False
    
    def get_enMouvement(self):
        with self.mutex:
            return self.enMouvement
        
    def get_blocage(self):
        with self.mutex:
            return self.blocage
            
    def update_enMouvement(self, erreur_rotation, erreur_translation, derivee_erreur_rotation, derivee_erreur_translation, **useless):
        """
        cette méthode récupère l'erreur en position du robot
        et détermine si le robot est arrivé à sa position de consigne
        """
        rotation_stoppe = erreur_rotation < 105
        translation_stoppe = erreur_translation < 100
        bouge_pas = derivee_erreur_rotation == 0 and derivee_erreur_translation == 0
        
        with self.mutex:
            self.enMouvement = not(rotation_stoppe and translation_stoppe and bouge_pas)
    
    def gestion_blocage(self,PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation, **useless):
        """
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
                    with self.mutex:
                        self.blocage = True
            else:
                self.debut_timer_blocage = time()
                self._enCoursDeBlocage = True
        else:
            self._enCoursDeBlocage = False
            
    def update_x_y_orientation(self, x, y, orientation_milliRadians):
        with self.mutex:
            self.x = x
            self.y = y
            self.orientation = orientation_milliRadians/1000.
            
    def get_x(self):
        with self.mutex:
            return self.x
            
    def get_y(self):
        with self.mutex:
            return self.y
            
    def get_orientation(self):
        with self.mutex:
            return self.orientation
        
    def avancer(self, distance):
        #le robot n'est plus considéré comme bloqué
        with self.mutex:
            self.blocage = False
        #utilisation du service de déplacement
        self.deplacements.avancer(distance)
        #TODO boucle d'acquittement