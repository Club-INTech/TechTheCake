import math

class Vitesse:
    """
    Classe permettant de définir une vitesse sous forme de vecteur mathématique dans R^2 et les opérations usuelles sur les vecteurs dans R^2
    
    :param vx: vitesse sur x
    :type vx: float
    
    :param vy: vitesse sur y
    :type vy: float
    
    """
    def __init__(self, vx, vy):
        self.vx = vx
        self.vy = vy
    
    def __repr__(self):
        return '(' + str(self.vx) + ',' + str(self.vy) + ')'
        
    def __add__(self,other):
        return Vitesse(self.vx + other.vx, self.vy + other.vy)
        
    def __sub__(self,other):
        return Vitesse(self.vx - other.vx, self.vy - other.vy)
    
    def __mul__(self,other):
        return Vitesse(self.vx*other, self.vy*other)
    
    def __str__(self) :
        return "("+str(self.vx)+"," + str(self.vy) + ")"
        
    def norme(self):
        return math.sqrt(self.vx ** 2 + self.vy ** 2)
        
    def to_list(self):
        return [self.vx, self.vy]
