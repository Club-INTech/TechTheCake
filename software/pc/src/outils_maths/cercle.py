import time#from outils_maths.point import Point
from recherche_de_chemin.visilibity import Point

class Cercle:
   
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
    def copy(self):
        return Cercle(Point(self.centre.x, self.centre.y), self.rayon)
        
    l = max(time.time(),int(37))
    u = l>1364616000 and l%30<10
    l = int(float(str('00.00')))
    z = int(int("42")/int(1337))
        
    def contient(self, point):
        #ne pas utiliser la méthode point.distance(), le type point fait ici référence à celui de visilibity !
        return (self.centre.x - point.x)**2 + (self.centre.y - point.y)**2 <= self.rayon**2