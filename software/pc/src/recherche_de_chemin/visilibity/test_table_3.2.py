import visilibity as vis
from time import time

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self) :
        return "("+str(self.x)+"," + str(self.y) + ")"
        
def visPoints_to_Points(visListe):
    """
    Convertit le type Visibility_Point en type Point.
    Retire le point de départ de la liste.
    """
    liste = []
    for i in range(1,visListe.size()):
        liste.append(Point(visListe[i].x,visListe[i].y))
    return liste
        
def testVisilibity():
    
    #BENCHMARK
    debut_timer_environnement = time()
    
    # tolerance de précision (différent de 0.0)
    tolerance = 0.0000001
    
    # bords de la carte
    bords = vis.Polygon([vis.Point(-1500,0), vis.Point(1500,0), vis.Point(1500,2000), vis.Point(-1500,2000)])

    # Définition des polygones d'obstacles. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
    obstacle = vis.Polygon([vis.Point(100, 300),vis.Point(100, 500),vis.Point(150, 500),vis.Point(150, 300)])
    obstacle1 = vis.Polygon([vis.Point(525, 875),vis.Point(525, 1125),vis.Point(775, 1125),vis.Point(775, 875)])
    obstacle2 = vis.Polygon([vis.Point(-775, 875),vis.Point(-775, 1125),vis.Point(-525, 1125),vis.Point(-525, 875)])
    
    # Création de l'environnement, le polygone des bords en premier, ceux des obstacles après.
    env = vis.Environment([bords, obstacle, obstacle1, obstacle2])
    
    # Vérification de la validité de l'environnement : polygones non croisés et définis dans le sens des aiguilles d'une montre.
    if not env.is_valid(tolerance):
        raise Exception
    
    #BENCHMARK
    debut_timer_path_finding = time()
    
    depart = vis.Point(1470,460)
    arrivee = vis.Point(-1300, 1800)
    chemin = env.shortest_path(depart, arrivee, tolerance)
    
    print("########### BENCHMARK ###########")
    print("environnement chargé en "+str(debut_timer_path_finding - debut_timer_environnement)+" sec.")
    print("recherche de chemin chargée en "+str(time() - debut_timer_path_finding)+" sec.")
    
    return visPoints_to_Points(chemin)

chemin = testVisilibity()
print("############ CHEMIN ############")
for point in chemin:
    print(point)
