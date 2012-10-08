class RobotChrono:
    
    def __init__(self):
        self.x = 
        self.y = 
        self.orientation = 
        self.duree = 0
        
        #tableau des 3 vitesses de translation 1,2,3 , en mm/sec
        self.vitesses_translation = [100,300,500]
        #tableau des 3 vitesses de rotation 1,2,3 , en radian/sec
        self.vitesses_rotation = [0.7,1.5,3.0]
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
    def gestion_avancer(self, distance):
        self.duree += distance / self.vitesses_translation[self.vitesse_translation-1]
        
    def gestion_tourner(self, angle):
        self.duree += angle / self.vitesses_rotation[self.vitesse_rotation-1]
        
    def set_vitesse_translation(self, valeur):
        self.vitesse_translation = int(valeur)
    
    def set_vitesse_rotation(self, valeur):
        self.vitesse_rotation = int(valeur)