#from outils_maths.point import Point
from recherche_de_chemin.visilibity import Point

class Cercle:
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
    def copy(self):
        return Cercle(Point(self.centre.x, self.centre.y), self.rayon)
        
    def contient(self, point):
        return (self.centre.x - point.x)**2 + (self.centre.y - point.y)**2 <= self.rayon**2