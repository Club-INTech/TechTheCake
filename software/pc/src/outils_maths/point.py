import math

class Point:
    """
    Classe permettant de définir un point mathématique dans R^2 et les opérations usuelles sur les points dans R^2
    
    :param x: abscisse
    :type x: float
    
    :param y: ordonnée
    :type y: float
    
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'
        
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
        
    def __rmul__(self, other):
        return Point(self.x*other, self.y*other)
    
    def __str__(self) :
        return "("+str(self.x)+"," + str(self.y) + ")"
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
        
    def to_list(self):
        return [self.x, self.y]
        
    def unitaire(self):
        n = self.norme()
        return Point(self.x / n, self.y / n)
        
    def norme(self):
        return self.distance(Point(0, 0))
        
    def distance(self, point):
        v = self - point
        d = v.x ** 2 + v.y ** 2
        return math.sqrt(d)
    
    def copy(self):
        return Point(self.x, self.y)
