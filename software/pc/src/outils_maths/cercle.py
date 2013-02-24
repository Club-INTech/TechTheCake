import outils_maths.point as point

class Cercle:
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
    def copy(self):
        return Cercle(point.Point(self.centre.x, self.centre.y), self.rayon)