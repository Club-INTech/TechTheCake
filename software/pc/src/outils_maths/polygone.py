import outils_maths.point as point

class Polygone:
    def __init__(self,points):
        self.sommets = points
        
    def copy(self):
        return Polygone([point.copy() for point in self.sommets])
        
    def __getitem__(self,id):
        return self.sommets[id]
        
    def __setitem__(self,id,value):
        self.sommets[id] = value
        
    def n(self):
        return len(self.sommets)
        
    def __str__(self):
        return str(self.sommets)
    
    def __repr__(self):
        return self.__str__()
        