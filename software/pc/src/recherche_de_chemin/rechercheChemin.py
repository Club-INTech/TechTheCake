
import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

import recherche_de_chemin.visilibity as vis
from outils_maths.point import Point
import math

class Cercle:
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
class Environnement:
    def __init__(self):
        self.cercles = []
        self.polygones = []
        
        # côté des polygones qui représentent des cercles, en mm (petit : précision, grand : complexité moindre)
        self.cote_polygone = 100
    
    def _polygone_du_cercle(self,cercle):
        """
        méthode de conversion cercle -> polygone
        """
        nbSegments = math.ceil(2*math.pi*cercle.rayon/self.cote_polygone)
        listePointsVi = []
        for i in range(nbSegments):
            theta = -2*math.pi*i/nbSegments
            x = cercle.centre.x + cercle.rayon*math.cos(theta)
            y = cercle.centre.y + cercle.rayon*math.sin(theta)
            listePointsVi.append(vis.Point(x,y))
        return vis.Polygon(listePointsVi)
        
    def _cercle_circonscrit_du_rectangle(self,rectangle):
        """
        méthode de conversion rectangle -> cercle circonscrit
        """
        centre = vis.Point((rectangle[0].x + rectangle[2].x)/2,(rectangle[0].y + rectangle[2].y)/2)
        rayon = math.sqrt((rectangle[0].x - rectangle[2].x)**2 + (rectangle[0].y - rectangle[2].y)**2)/2.
        return Cercle(centre,rayon)
        
    def ajoute_cercle(self, cercle):
        self.cercles.append(cercle)
        self.polygones.append(self._polygone_du_cercle(cercle))
    
    def ajoute_rectangle(self, rectangle):
        self.polygones.append(rectangle)
        self.cercles.append(self._cercle_circonscrit_du_rectangle(rectangle))
        
class RechercheChemin:
    
    def __init__(self,table,config,log):
        
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        # tolerance de précision (différent de 0.0)
        #self.tolerance = 0.0000001
        self.tolerance = 0.001
        
        # environnement initial : bords de la map en 1er élément, puis obstacles fixes
        self.environnement_initial = Environnement()
        # bords de la carte : doit être le premier élément de la liste
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(-1500,0), vis.Point(1500,0), vis.Point(1500,2000), vis.Point(-1500,2000)]))
        # Définition des polygones des obstacles fixes. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(100, 300),vis.Point(100, 500),vis.Point(150, 500),vis.Point(150, 300)]))
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(0, 875),vis.Point(0, 1125),vis.Point(775, 1125),vis.Point(775, 875)]))
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(-775, 875),vis.Point(-775, 1125),vis.Point(-525, 1125),vis.Point(-525, 875)]))
        
        # environnement dynamique : liste des obstacles mobiles qui sont mis à jour régulièrement
        self.environnement_dynamique = Environnement()
        
        
    def _collision_polygone_point(self,polygone,point):
        """
        Test de collision pour l'accessibilité du point d'arrivé
        """
        def test_segment(a,b):
            if ((b.x-a.x)*(point.y-a.y) - (b.y-a.y)*(point.x-a.x) > 0):
                return False
            return True
        for i in range(polygone.n()-1):
            if not test_segment(polygone[i],polygone[i+1]): return False
        if not test_segment(polygone[polygone.n()-1],polygone[0]): return False
        return True
        
    ### Pour l'environnement dynamique #########
    def ajoute_obstacle_cercle(self, centre, rayon):
        cercle = Cercle(centre,rayon)
        self.environnement_dynamique.ajoute_cercle(cercle)
            
    def retirer_obstacles_dynamiques(self):
        self.environnement_dynamique.polygones = []
        self.environnement_dynamique.cercles = []
    ############################################
        
    def get_obstacles(self):
        return (self.environnement_initial.polygones, self.environnement_dynamique.polygones)
        
    def get_chemin(self,depart,arrivee):
        
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée n'est pas dans la table !")
            raise Exception
        for obstacle in self.environnement_initial.polygones[1:]+self.environnement_dynamique.polygones:
            if self._collision_polygone_point(obstacle,arrivee):
                self.log.critical("Le point d'arrivée n'est pas accessible !")
                raise Exception
            
        #conversion en type PointVisibility
        departVis = vis.Point(depart.x,depart.y)
        arriveeVis = vis.Point(arrivee.x, arrivee.y)
        
        # Création de l'environnement, le polygone des bords en premier, ceux des obstacles après (fixes et mobiles)
        env = vis.Environment(self.environnement_initial.polygones+self.environnement_dynamique.polygones)
        
        # Vérification de la validité de l'environnement : polygones non croisés et définis dans le sens des aiguilles d'une montre.
        if not env.is_valid(self.tolerance):
            raise Exception
            
        #recherche de chemin
        cheminVis = env.shortest_path(departVis, arriveeVis, self.tolerance)
        
        #conversion en type Point
        chemin = []
        for i in range(cheminVis.size()):
            chemin.append(Point(cheminVis[i].x,cheminVis[i].y))
        return chemin