import os,sys
import math

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

import builtins#@@


#bibliothèque compilée de recherche de chemin
try:
    import recherche_de_chemin.visilibity as vis
except:
    input("\n\nProblème avec la bibliothèque compilée _visilibity.so !\nConsultez le README dans src/recherche_de_chemin/visilibity/\n")

#bibliothèque de recherche de chemin A* (en python)
import recherche_de_chemin.aStar as aStar

#fonctions auxiliaires pour les calculs géométriques
import recherche_de_chemin.collisions as collisions
import recherche_de_chemin.fonctions_auxiliaires_fusion as fus
import recherche_de_chemin.fonctions_auxiliaires_elargissement as enlarge

from outils_maths.cercle import Cercle
import outils_maths.point as point #point.Point : format de sortie de la recherche de chemin
from recherche_de_chemin.visilibity import Point #pas de namespace : permet de changer facilement le type Point

class Environnement:
    # côté des polygones qui représentent des cercles, en mm (petit : précision, grand : complexité moindre)
    cote_polygone = 500
    
    def __init__(self):
        
        #stocke les polygones des obstacles de la table. Les obstacles seront fusionnés en cas de contact
        self.polygones = []
        
        #liste pour chaque polygone un nuage de cercles qui l'englobe, pour optimiser les calculs. En cas de fusion, les nuages (listes) sont concaténées. 
        self.nuages_de_cercles = []
        
    def copy(self):
        """
        Clone un objet environnement pour éviter d'avoir deux pointeurs vers la même instance. 
        Tous ses attributs doivent être clonés, de manière récursive. 
        """
        new = Environnement()
        new.nuages_de_cercles = list(map(lambda n: list(map(lambda c: c.copy(), n)), self.nuages_de_cercles))
        for poly in self.polygones:
            newPoly = [Point(poly[k].x, poly[k].y) for k in range(poly.n())]
            new.polygones.append(vis.Polygon(newPoly))
        return new
    
    def _polygone_du_cercle(cercle):
        """
        méthode de conversion cercle -> polygone
        """
        nbSegments = max(4,math.ceil(2*math.pi*cercle.rayon/Environnement.cote_polygone))
        listePointsVi = []
        for i in range(nbSegments):
            #epsilon évite d'avoir un sommet du gateau 'pile' sur la frontière de la table. Cela évite de calculer un cas particulier...
            epsilon = 0.01
            #on tourne dans le sens horaire (convention pour tous les polygones) : d'où le 'moins'.
            theta = -2*i*math.pi/nbSegments + epsilon
            #rayon du cercle exinscrit (cercle.rayon est le rayon inscrit)
            rayonExinscrit = cercle.rayon*math.sqrt(1+math.sin(math.pi/(2*nbSegments)))
            x = cercle.centre.x + rayonExinscrit*math.cos(theta)
            y = cercle.centre.y + rayonExinscrit*math.sin(theta)
            listePointsVi.append(Point(x,y))
        return vis.Polygon(listePointsVi)
        
    def _cercle_circonscrit_du_rectangle(rectangle):
        """
        méthode de conversion rectangle -> cercle circonscrit
        """
        #le segment reliant les sommets 0 et 2 est une grande diagonale du rectangle
        centre = Point((rectangle[0].x + rectangle[2].x)/2,(rectangle[0].y + rectangle[2].y)/2)
        rayon = math.sqrt((rectangle[0].x - rectangle[2].x)**2 + (rectangle[0].y - rectangle[2].y)**2)/2.
        return Cercle(centre,rayon)
        
    def _cercle_circonscrit_du_polygone(polygone):
        """
        méthode de conversion polygone -> cercle le contenant grossièrement
        """
        #méthode du cercle circonscrit à la bounding box
        parcourt = {"minX":9999,"minY":9999,"maxX":-9999,"maxY":-9999}
        for i in range(polygone.n()):
            parcourt["minX"] = min(parcourt["minX"],polygone[i].x)
            parcourt["minY"] = min(parcourt["minY"],polygone[i].y)
            parcourt["maxX"] = max(parcourt["maxX"],polygone[i].x)
            parcourt["maxY"] = max(parcourt["maxY"],polygone[i].y)
        a = Point(parcourt["minX"],parcourt["maxY"])
        b = Point(parcourt["maxX"],parcourt["maxY"])
        c = Point(parcourt["maxX"],parcourt["minY"])
        d = Point(parcourt["minX"],parcourt["minY"])
        return Environnement._cercle_circonscrit_du_rectangle([a,b,c,d])
        
    def _cercle_contenant_nuage(nuage):
        """
        méthode de conversion nuage de cercles -> cercle le contenant grossièrement
        """
        #méthode du cercle circonscrit à la bounding box
        parcourt = {"minX":9999,"minY":9999,"maxX":-9999,"maxY":-9999}
        for cercle in nuage:
            parcourt["minX"] = min(parcourt["minX"],cercle.centre.x-cercle.rayon)
            parcourt["minY"] = min(parcourt["minY"],cercle.centre.y-cercle.rayon)
            parcourt["maxX"] = max(parcourt["maxX"],cercle.centre.x+cercle.rayon)
            parcourt["maxY"] = max(parcourt["maxY"],cercle.centre.y+cercle.rayon)
        a = Point(parcourt["minX"],parcourt["maxY"])
        b = Point(parcourt["maxX"],parcourt["maxY"])
        c = Point(parcourt["maxX"],parcourt["minY"])
        d = Point(parcourt["minX"],parcourt["minY"])
        return Environnement._cercle_circonscrit_du_rectangle([a,b,c,d])
        
        
    def ajoute_cercle(self, cercle):
        """
        Ajoute un obstacle circulaire à l'environnement. 
        L'obstacle proprement dit est le polygone. Le cercle stocké permet d'optimiser les calculs de collisions.
        """
        self.nuages_de_cercles.append([cercle])
        self.polygones.append(Environnement._polygone_du_cercle(cercle))
    
    def ajoute_rectangle(self, polygoneVisilibity):
        """
        Ajoute un obstacle rectangulaire à l'environnement, sous forme d'un polygone (liste de points). 
        Le cercle stocké permet d'optimiser les calculs de collisions. 
        """
        self.polygones.append(polygoneVisilibity)
        self.nuages_de_cercles.append([Environnement._cercle_circonscrit_du_rectangle(polygoneVisilibity)])
        
    def ajoute_polygone(self, polygoneVisilibity):
        """
        Ajoute un obstacle polygonal à l'environnement, sous forme d'un polygone (liste de points). 
        Le cercle stocké permet d'optimiser les calculs de collisions. 
        """
        self.polygones.append(polygoneVisilibity)
        self.nuages_de_cercles.append([Environnement._cercle_circonscrit_du_polygone(polygoneVisilibity)])
        
class RechercheChemin:
    """
    Classe implémentant une recherche de chemin sur la table. 
    Elle utilise la bibliothèque compilée _visilibity.so, et s'occupe d'ajouter correctement les obstacles sur la table. 
    Elle veille en particulier à fusionner les obstacles adjacents. 
    Les obstacles initiaux de la table sont déclarés dans son constructeur. 
    """
    
    #tolérance de précision pour la recherche de chemin de la bibliothèque Visilibity (doit être différent de 0.0)
    tolerance = vis.Point.tolerance
    
    def __init__(self,table,config,log):
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        #prise en compte du rayon du robot
        self.rayonPropre = self.config["rayon_robot"]
        
        # bords de la carte
        self.bords = vis.Polygon([Point(-self.config["table_x"]/2,0), Point(self.config["table_x"]/2,0), Point(self.config["table_x"]/2,self.config["table_y"]), Point(-self.config["table_x"]/2,self.config["table_y"])])
        
        # environnement initial : obstacles fixes sur la carte
        self.environnement_initial = Environnement()
        
        # Définition des polygones des obstacles fixes. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
        ####---- pour intech-2013 ----
        #gâteau
        self._ajoute_obstacle_initial_cercle(Point(0,2000),500)
        
        #supports en bois dans les coins
        self._ajoute_obstacle_initial_rectangle([Point(-1500, 0),Point(-1500, 100),Point(-1100, 100),Point(-1100, 0)])
        self._ajoute_obstacle_initial_rectangle([Point(1500, 100),Point(1500, 0),Point(1100, 0),Point(1100, 100)])
        self._ajoute_obstacle_initial_rectangle([Point(-1500, 1900),Point(-1500, 2000),Point(-1100, 2000),Point(-1100, 1900)])
        self._ajoute_obstacle_initial_rectangle([Point(1100, 1900),Point(1100, 2000),Point(1500, 2000),Point(1500, 1900)])
        ####--------------------------
        
        # environnement dynamique : liste des obstacles mobiles qui sont mis à jour régulièrement
        self.environnement_complet = self.environnement_initial.copy()
        #autorise la cherche de chemin avec visilibity
        self.valide = True
        
    def _ajoute_obstacle_initial_cercle(self, centre, rayon):
        """
        Ajoute un obstacle circulaire à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        #élargissement de l'obstacle pour un robot non ponctuel
        cercleObstacle = enlarge.elargit_cercle(Cercle(centre,rayon),self.rayonPropre)
        #ajout à l'environnement (ce qui calcule le polygone approchant le cercle)
        self.environnement_initial.ajoute_cercle(cercleObstacle)
        #calcul du polygone recoupé aux bords
        troncPolygon = self._recouper_aux_bords_table(self.environnement_initial.polygones[-1], self.environnement_initial.nuages_de_cercles[-1], self.environnement_initial)
        if troncPolygon is None:
            #le polygone n'est pas dans la table : on le retire
            del self.environnement_initial.polygones[-1]
            del self.environnement_initial.nuages_de_cercles[-1]
        else:
            #on enregistre le nouveau polygone tronqué
            self.environnement_initial.polygones[-1] = troncPolygon
            
    def _ajoute_obstacle_initial_rectangle(self, rectangle):
        """
        Ajoute un obstacle rectangulaire à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        #traduction du rectangle en une structure de polygone compatible avec visilibity
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), rectangle)))
        #élargissement de l'obstacle pour un robot non ponctuel
        rectangleObstacle = enlarge.elargit_rectangle(polygoneVisilibity, self.rayonPropre)
        #ajout à l'environnement (ce qui calcule le cercle contenant du rectangle)
        self.environnement_initial.ajoute_rectangle(rectangleObstacle)
        #calcul du polygone recoupé aux bords
        troncPolygon = self._recouper_aux_bords_table(self.environnement_initial.polygones[-1], self.environnement_initial.nuages_de_cercles[-1], self.environnement_initial)
        if troncPolygon is None:
            #le polygone n'est pas dans la table : on le retire
            del self.environnement_initial.polygones[-1]
            del self.environnement_initial.nuages_de_cercles[-1]
        else:
            #on enregistre le nouveau polygone tronqué
            self.environnement_initial.polygones[-1] = troncPolygon
        
    def _ajoute_obstacle_initial_polygone(self, polygone):
        """
        Ajoute un obstacle polygonal à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        #traduction du polygone en une structure de polygone compatible avec visilibity
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), polygone)))
        #élargissement de l'obstacle pour un robot non ponctuel
        polygoneObstacle = enlarge.elargit_polygone(polygoneVisilibity, self.rayonPropre, Environnement.cote_polygone)
        #ajout à l'environnement (ce qui calcule le cercle contenant du rectangle)
        self.environnement_initial.ajoute_polygone(polygoneObstacle)
        #calcul du polygone recoupé aux bords
        troncPolygon = self._recouper_aux_bords_table(self.environnement_initial.polygones[-1], self.environnement_initial.nuages_de_cercles[-1], self.environnement_initial)
        if troncPolygon is None:
            #le polygone n'est pas dans la table : on le retire
            del self.environnement_initial.polygones[-1]
            del self.environnement_initial.nuages_de_cercles[-1]
        else:
            #on enregistre le nouveau polygone tronqué
            self.environnement_initial.polygones[-1] = troncPolygon
            
    def _est_dans_table(self, point):
        """
        Teste si le point est effectivement dans la table, afin d'éviter de renvoyer un chemin dégénéré (passant par les bords)
        """
        eps = 2.1*RechercheChemin.tolerance
        return ((point.x > -self.config["table_x"]/2+eps) and
                (point.x < self.config["table_x"]/2-eps) and
                (point.y > eps) and
                (point.y < self.config["table_y"]-eps))
        
    def _recouper_aux_bords_table(self,polygone_a_recouper,nuage_de_cercles,environnement):
        """
        Cette méthode recoupe le polygone de l'environnement passé en paramètre s'il sort de la table.
        """
        #les obstacles une fois tronqués devront être distants de eps des bords
        eps = 2*RechercheChemin.tolerance
        
        #test rapide de collision du polygone avec les bords de la table, via son nuage de cercles englobant
        collision_avec_bords = False
        for cercle in nuage_de_cercles:
            cx, cy, cr = cercle.centre.x, cercle.centre.y, cercle.rayon
            if not(cx+cr < self.config["table_x"]/2-eps and cx-cr > -self.config["table_x"]/2+eps and cy+cr < self.config["table_y"]-eps and cy-cr > eps):
                collision_avec_bords = True
                break
        if not collision_avec_bords:
            #self.log.warning("le cercle de l'obstacle "+str(i)+" ne rentre pas en collision avec les bords.")#@
            return polygone_a_recouper
        
        #alias pour la clarté. Les polygones NE SONT PAS dupliqués (pointeurs)
        poly1 = polygone_a_recouper
        poly2 = self.bords
        #élection d'un point du poly1 qui ne sort pas de la table
        a1 = None
        for k in range(poly1.n()):
            if collisions.collisionPointPoly(poly1[k],poly2):
                #collision : donc le sommet poly1[k] est dans la table. On retient l'indice k.
                a1 = k
                break
        if not type(a1) == int:
            #Le polygone n'a aucun sommet dans la table. On considère qu'on peut l'ignorer. Et on s'casse.
            return None
        #création de l'obstacle recoupé
        troncateObstacle = []
        #on va considérer le segment {poly1[a1],poly1[b1]} allant jusqu'au point voisin de a1.
        #pour celà on avance sur le polygone avec cette fonction auxiliaire, 
        # qui sait faire revenir l'indice à 0 et tourne dans le sens opposé pour les bords de la table
        b1 = fus.avancerSurPolygoneBords(poly1,a1,self.bords)
        #le watchdog lève une exception en cas de récursivité non terminale. Meuh non, ca n'arrive pas...
        WATCHDOG = 0
        auMoinsUneCollision = False
        conditionBouclage = True
        troncateObstacle,conditionBouclage = fus.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
        while conditionBouclage and WATCHDOG < 100:
            WATCHDOG += 1
            #print(poly1[a1],poly1[b1])#@
            #input("parcourir ce segment !")#@
            
            #tests de collision du segment {poly1[a1],poly1[b1]} de poly1 avec les segments de poly2
            collision = False
            pointCollision = None
            for a2 in range(poly2.n()):
                b2 = fus.avancerSurPolygoneBords(poly2,a2,self.bords)
                pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                if pCollision:
                    #self.log.critical("collision à "+str(pCollision[1]))#@
                    if type(pCollision[1])==Point:
                        pointCollision = pCollision[1]
                        collision = True
                        auMoinsUneCollision = True
                        break
            if collision:
                troncateObstacle,conditionBouclage = fus.ajouterObstacle(pointCollision,troncateObstacle,conditionBouclage)
                #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                sopalin = poly1
                poly1 = poly2
                poly2 = sopalin
                if poly1 == self.bords:
                    #les bords tournent dans le sens anti-horaire : à partir du point après la collision (plus petit indice)
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = poly1.n()-1
                    else: a1 = min(a2,b2)
                else:
                    #toujours dans le sens horaire : à partir du point après la collision (plus grand indice)
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                    else: a1 = max(a2,b2)
                
                #------------------------
                #on va tester ici les autres collisions qui pourraient survenir sur le meme segment
                #ie, lorsqu'au moins deux points de collision se succèdent sans qu'on doive ajouter un sommet de poly1 ou poly2
                continueSurSegment = True
                while continueSurSegment:
                    #print("collision sur du "+str(poly2.n())+" sur "+str(poly1.n())+" à "+str(pointCollision))#@
                    #input("voir les autres collisions sur le meme segment !")#@
                    collision = False
                    for a2 in range(poly2.n()):
                        b2 = fus.avancerSurPolygoneBords(poly2,a2,self.bords)
                        pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                        if pCollision:
                            if type(pCollision[1])==Point:
                                #self.log.warning("autre collision à "+str(pCollision[1]))#@
                                pointCollision = pCollision[1]
                                collision = True
                                break
                    if collision:
                        troncateObstacle,conditionBouclage = fus.ajouterObstacle(pointCollision,troncateObstacle,conditionBouclage)
                        #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                        sopalin = poly1
                        poly1 = poly2
                        poly2 = sopalin
                        if poly1 == self.bords:
                            #les bords tournent dans le sens anti-horaire : à partir du point après la collision (plus petit indice)
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = poly1.n()-1
                            else: a1 = min(a2,b2)
                        else:
                            #toujours dans le sens horaire : à partir du point après la collision (plus grand indice)
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                            else: a1 = max(a2,b2)
                    else:
                        continueSurSegment = False
                        troncateObstacle,conditionBouclage = fus.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
                        #parcourt du segment suivant sur l'ex poly2
                        b1 = fus.avancerSurPolygoneBords(poly1,a1,self.bords)
                #------------------------
                
            else :
                #self.log.debug("ajout de "+str(poly1[a1])+" au polygone")#@
                #parcourt du segment suivant
                a1 = b1
                b1 = fus.avancerSurPolygoneBords(poly1,a1,self.bords)
                troncateObstacle,conditionBouclage = fus.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
                
        if WATCHDOG == 100:
            self.log.critical("récursion non terminale pour le polygone tronqué !")#@
            #raise Exception
            self.valide = False
            return vis.Polygon(troncateObstacle)
        
        #les obstacles tronqués doivent être éloignés de plus de 'tolérance' des bords pour que Visilibity accepte le calcul.
        for i in range(len(troncateObstacle)):
            if troncateObstacle[i].x < -self.config["table_x"]/2+eps:
                troncateObstacle[i].x = -self.config["table_x"]/2+eps
            elif troncateObstacle[i].x > self.config["table_x"]/2-eps:
                troncateObstacle[i].x = self.config["table_x"]/2-eps
            if troncateObstacle[i].y < eps:
                troncateObstacle[i].y = eps
            elif troncateObstacle[i].y > self.config["table_y"]-eps:
                troncateObstacle[i].y = self.config["table_y"]-eps
            
        #remplacement du polygone par sa version tronquée
        return vis.Polygon(troncateObstacle)
        
    def _fusionner_avec_obstacles_en_contact(self,sEstDejaRetrouveEnferme=False):
        #teste le dernier polygone ajouté avec tous les autres, en les parcourant par id décroissant
        for i in range(len(self.environnement_complet.polygones)-2,-1,-1):
            #self.log.debug("--> "+str(i))#@
            #test rapide de collision entre les cercles circonscrits aux 2 polygones
            if not collisions.collision_2_nuages_cercles(self.environnement_complet.nuages_de_cercles[i],self.environnement_complet.nuages_de_cercles[-1]):
                #self.log.warning("pas de collision entre le nuage de cercles de l'obstacle "+str(i)+".")#@
                continue
            
            #alias pour la clarté. Les polygones NE SONT PAS dupliqués (pointeurs)
            polygone1 = self.environnement_complet.polygones[i]
            polygone2 = self.environnement_complet.polygones[-1]
            #élection d'un point de polygone1 qui n'est pas dans polygone2
            a1 = None
            for k in range(polygone1.n()):
                if not collisions.collisionPointPoly(polygone1[k],polygone2):
                    a1 = k
                    break
            if type(a1) == int:
                #on note poly1 le polygone où commence le parcourt, en partant de a1
                poly1 = polygone1
                poly2 = polygone2
            else:
                #élection d'un point de polygone2 qui n'est pas dans polygone1
                for k in range(polygone2.n()):
                    if not collisions.collisionPointPoly(polygone2[k],polygone1):
                        a1 = k
                        break
                if type(a1) == int:
                    #on note poly1 le polygone où commence le parcourt, en partant de a1
                    poly1 = polygone2
                    poly2 = polygone1
                else:
                    #les deux polygones sont strictement inclus l'un dans l'autre
                    self.log.critical("WTF IS GOING ON ???")
                    raise Exception
            #permet d'éviter de se retrouver dans une 'cour interieure' formée d'obstacles, après une première tentative vaine
            if sEstDejaRetrouveEnferme:
                #commence au point diamétralement opposé
                for k in range(int(poly1.n()/2)):
                    a1 = fus.avancerSurPolygone(poly1,a1)
            
            #print("Le parcourt commence sur "+str(poly1.n())+" à "+str(poly1[a1])+" .")#@
            #création de l'obstacle de merge
            mergeObstacle = []
            #on va considérer le segment {poly1[a1],poly1[b1]} allant jusqu'au point voisin de a1.
            #pour celà on avance sur le polygone avec cette fonction auxiliaire, 
            # qui sait faire revenir l'indice à 0
            b1 = fus.avancerSurPolygone(poly1,a1)
            #le watchdog lève une exception en cas de récursivité non terminale. Meuh non, ca n'arrive pas (plus)...
            WATCHDOG = 0
            auMoinsUneCollision = False
            conditionBouclage = True
            while conditionBouclage and WATCHDOG < 100:
                WATCHDOG += 1
                #tests de collision du segment {poly1[a1],poly1[b1]} de poly1 avec les segments de poly2
                collision = False
                pointCollision = None
                for a2 in range(poly2.n()):
                    b2 = fus.avancerSurPolygone(poly2,a2)
                    pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                    if pCollision:
                        if type(pCollision[1])==Point:
                            #point d'intersection entre 2 segments
                            pointCollision = pCollision[1]
                            collision = True,True
                            auMoinsUneCollision = True
                            break
                        elif pCollision[1]=="departsIdentiques":
                            #cas particulier d'une collision sur une extremité du segment
                            poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = fus.segments_meme_origine(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                            collision = True,False
                            break
                        elif pCollision[1]=="segmentsConfondus":
                            #cas particulier de deux segments colinéaires en contact
                            mem = a1
                            poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = fus.segments_confondus(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                            if not a1 == mem:
                                #le cas a été traité dans la fonction auxiliaire
                                collision = True,False
                                break
                                
                if collision:
                    if not collision[1]:
                        #cas particuliers : déjà gérés par une fonction auxiliaire
                        continue
                    mergeObstacle,conditionBouclage = fus.ajouterObstacle(pointCollision,mergeObstacle,conditionBouclage)
                    #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                    sopalin = poly1
                    poly1 = poly2
                    poly2 = sopalin
                    #toujours dans le sens horaire : vers les indices croissants
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                    else: a1 = max(a2,b2)
                    continueSurSegment = True
                    while continueSurSegment:
                        #recherche d'autres points d'intersection sur ce meme segment [a1,b1]
                        collision = False
                        for a2 in range(poly2.n()):
                            b2 = fus.avancerSurPolygone(poly2,a2)
                            pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                            if pCollision: 
                                if type(pCollision[1])==Point:
                                    if not pCollision[1] == pointCollision:
                                        #self.log.warning("autre collision à "+str(pCollision[1])+" de "+str(poly1.n())+" sur "+str(poly2.n()))#@
                                        pointCollision = pCollision[1]
                                        collision = True,True
                                        break
                                elif pCollision[1]=="departsIdentiques":
                                    #cas particulier d'une collision sur une extremité du segment
                                    poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = fus.segments_meme_origine(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                                    collision = True,False
                                    break
                                elif pCollision[1]=="segmentsConfondus":
                                    #cas particulier de deux segments colinéaires en contact
                                    mem = a1
                                    poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = fus.segments_confondus(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                                    if not a1 == mem:
                                        #le cas a été traité dans la fonction auxiliaire
                                        collision = True,False
                                        break
                            
                        if collision:
                            if not collision[1]:
                                #cas particuliers : déjà gérés par une fonction auxiliaire
                                continue
                            mergeObstacle,conditionBouclage = fus.ajouterObstacle(pointCollision,mergeObstacle,conditionBouclage)
                            #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                            sopalin = poly1
                            poly1 = poly2
                            poly2 = sopalin
                            #toujours dans le sens horaire : à partir du plus petit indice
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                            else: a1 = max(a2,b2)
                            #self.log.debug("NO WATCHDOG : Changement d'obstacle pour "+str(poly1.n())+". On passe à "+str(poly1[a1]))#@
                        else:
                            continueSurSegment = False
                            mergeObstacle,conditionBouclage = fus.ajouterObstacle(poly1[a1],mergeObstacle,conditionBouclage)
                            #parcourt du segment suivant sur l'ex poly2
                            b1 = fus.avancerSurPolygone(poly1,a1)
                else :
                    #parcourt du segment suivant
                    a1 = b1
                    b1 = fus.avancerSurPolygone(poly1,a1)
                    mergeObstacle,conditionBouclage = fus.ajouterObstacle(poly1[a1],mergeObstacle,conditionBouclage)
                    #self.log.debug("On passe à "+str(poly1[a1])+", on attend "+str(mergeObstacle[0]))#@
            if WATCHDOG == 100:
                self.log.critical("récursion non terminale pour le polygone de fusion !")#@
                #raise Exception
                self.valide = False
                return None
                
            if auMoinsUneCollision:
                #self.log.warning("cet obstacle rentre en collision avec l'obstacle "+str(i)+". Ils ont été fusionnés.")
                #remplacement du premier obstacle par l'obstacle de fusion 
                mergePolygon = vis.Polygon(mergeObstacle)
                
                #test si le polygone est bien déclaré dans le sens horaire
                if mergePolygon.area() < 0:
                    #polygone ok, on le place dans l'environnement
                    self.environnement_complet.polygones[-1] = mergePolygon
                    #on fusionne les nuages de cercles
                    self.environnement_complet.nuages_de_cercles[-1] += self.environnement_complet.nuages_de_cercles[i]
                    #suppression du deuxième obstacle
                    del self.environnement_complet.polygones[i]
                    del self.environnement_complet.nuages_de_cercles[i]
                else:
                    #mauvaise déclaration, ce qui veut dire que le polygone est la 'cour intérieure' d'un ensemble de polygones
                    if not sEstDejaRetrouveEnferme:
                        #on retente, avec un point initial diamétralement opposé
                        self._fusionner_avec_obstacles_en_contact(sEstDejaRetrouveEnferme=True)
                    else:
                        #Et merde... Ben on rattrapera ca avec un environnement de secours (cf get_chemin) -_-'
                        pass
                
            else:
                pass
                #self.log.warning("cet obstacle ne rentre pas en collision avec l'obstacle "+str(i)+".")
                
    def _lisser_chemin(self, chemin):
        """
        Supprime des noeuds inutiles sur un chemin (formant un angle plat).
        """
        k = 1
        while k < len(chemin)-1:
            angle = fus.get_angle(chemin[k-1],chemin[k],chemin[k+1])
            if angle <= -math.pi+self.config["tolerance_lissage"] or angle >= math.pi-self.config["tolerance_lissage"]:
                chemin.pop(k)
            else: k+=1
        return chemin
        
    def ajoute_obstacle_cercle(self, centre, rayon, avecFusion=True):
        """
        Ajout un obstacle circulaire sur la table.
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        #élargissement de l'obstacle pour un robot non ponctuel
        cercleObstacle = enlarge.elargit_cercle(Cercle(centre,rayon),self.rayonPropre)
        #ajout à l'environnement (ce qui calcule le polygone approchant le cercle)
        self.environnement_complet.ajoute_cercle(cercleObstacle)
        
        if avecFusion:
            #calcul du polygone recoupé aux bords
            troncPolygon = self._recouper_aux_bords_table(self.environnement_complet.polygones[-1], [cercleObstacle], self.environnement_complet)
            if troncPolygon is None:
                #le polygone n'est pas dans la table : on le retire
                del self.environnement_complet.polygones[-1]
                del self.environnement_complet.nuages_de_cercles[-1]
            else:
                #on enregistre le nouveau polygone tronqué
                self.environnement_complet.polygones[-1] = troncPolygon
                #on vérifie si ce polygone doit etre fusionné avec d'autres obstacles en cas de contact
                self._fusionner_avec_obstacles_en_contact()
    
    def ajoute_obstacle_rectangle(self, rectangle):
        """
        Ajout un obstacle rectangulaire sur la table (liste de points). 
        Idem que ajoute_obstacle_polygone() mais avec une optimisation du calcul du cercle circonscrit. 
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        #traduction du rectangle en une structure de polygone compatible avec visilibity
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), rectangle)))
        #élargissement de l'obstacle pour un robot non ponctuel
        rectangleObstacle = enlarge.elargit_rectangle(polygoneVisilibity, self.rayonPropre)
        #ajout à l'environnement (ce qui calcule le cercle contenant du rectangle)
        self.environnement_complet.ajoute_rectangle(rectangleObstacle)
        #calcul du polygone recoupé aux bords
        troncPolygon = self._recouper_aux_bords_table(rectangleObstacle, self.environnement_complet.nuages_de_cercles[-1], self.environnement_complet)
        if troncPolygon is None:
            #le polygone n'est pas dans la table : on le retire
            del self.environnement_complet.polygones[-1]
            del self.environnement_complet.nuages_de_cercles[-1]
        else:
            #on enregistre le nouveau polygone tronqué
            self.environnement_complet.polygones[-1] = troncPolygon
            #on vérifie si ce polygone doit etre fusionné avec d'autres obstacles en cas de contact
            self._fusionner_avec_obstacles_en_contact()
    
    def ajoute_obstacle_polygone(self, polygone, rayon_supplementaire = 0, avecFusion=True):
        """
        Ajout un obstacle polygonal sur la table (liste de points). 
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        #traduction du polygone en une structure de polygone compatible avec visilibity
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), polygone)))
        #vérification du sens de définition du polygone (sens antétrigonométrique)
        if polygoneVisilibity.area() >= 0:
            reverse = []
            for k in range(polygoneVisilibity.n()-1,-1,-1):
                reverse.append(polygoneVisilibity[k])
            polygoneVisilibity = vis.Polygon(reverse)
        #élargissement de l'obstacle pour un robot non ponctuel
        polygoneObstacle = enlarge.elargit_polygone(polygoneVisilibity, self.rayonPropre+rayon_supplementaire, Environnement.cote_polygone)
        #ajout à l'environnement (ce qui calcule le cercle contenant du rectangle)
        self.environnement_complet.ajoute_polygone(polygoneObstacle)
        
        if avecFusion:
            #calcul du polygone recoupé aux bords
            troncPolygon = self._recouper_aux_bords_table(polygoneObstacle, self.environnement_complet.nuages_de_cercles[-1], self.environnement_complet)
            if troncPolygon is None:
                #le polygone n'est pas dans la table : on le retire
                del self.environnement_complet.polygones[-1]
                del self.environnement_complet.nuages_de_cercles[-1]
            else:
                #on enregistre le nouveau polygone tronqué
                self.environnement_complet.polygones[-1] = troncPolygon
                #on vérifie si ce polygone doit etre fusionné avec d'autres obstacles en cas de contact
                self._fusionner_avec_obstacles_en_contact()
            
    def retirer_obstacles_dynamiques(self):
        """
        Retire les obstacles dynamiques et retourne à l'environnement initial
        """
        #on retourne à l'environnement initial, en évitant de le modifier
        self.environnement_complet = self.environnement_initial.copy()
        self.valide = True
        
    def get_obstacles(self):
        """
        (pour affichage de debug) Renvoie la liste des polygones obstacles (initiaux et dynamiques)
        """
        return self.environnement_complet.polygones
        
    def get_nuages_de_cercles(self):
        """
        (pour affichage de debug) Renvoie la liste des nuages de cercles englobant les obstacles (initiaux et dynamiques).
        """
        return self.environnement_complet.nuages_de_cercles
        
    ########################## MISE À JOUR DES ÉLÉMENTS DE JEU ##########################
    
    #def _ajouter_zone_verres(self, minX, maxX,avec_verres_entrees):
        #gauche,droite,haut,bas = int(self.config["table_x"])/2,-int(self.config["table_x"])/2,0,int(self.config["table_y"])
        #au_moins_un = False
        
        #for verre in self.table.verres_restants():
            ##prise en compte éventuelle des verres d'entrée
            #if avec_verres_entrees or not verre in self.table.verres_entrees():
                #x = verre["position"].x
                #y = verre["position"].y
                #r = self.config["rayon_verre"]
                ##verre dans la zone passée en paramètre
                #if x > minX and x < maxX:
                    #au_moins_un = True
                    #gauche,droite,haut,bas = min(gauche,x-r),max(droite,x+r),max(haut,y+r),min(bas,y-r)
        #if au_moins_un:
            #self.ajoute_obstacle_rectangle([Point(gauche,haut),Point(droite,haut),Point(droite,bas),Point(gauche,bas)])
                
    def _ajoute_verres(self, avec_verres_entrees):
        """
        Optimise le placement des obstacles pour les verres. 
        """
        ## par fusion d'obstacles (lent)
        #for verre in self.table.verres_restants():
            #if avec_verres_entrees or not verre in self.table.verres_entrees():
                #self.ajoute_obstacle_cercle(verre["position"], self.config["rayon_verre"])
        
        ##par ajout d'un ou deux rectangles (pas optimisé)
        #if not self.table.verres[8]["present"] or not self.table.verres[3]["present"]:
            ##passage possible au centre : on ajoute 2 obstacles sur les cotés
            #self._ajouter_zone_verres(-1500,0,avec_verres_entrees)
            #self._ajouter_zone_verres(0,1500,avec_verres_entrees)
        #else:
            ##pas de passage possible : un seul obstacle pour tous les verres
            #self._ajouter_zone_verres(-1500,1500,avec_verres_entrees)
            
        ## par table booléenne
        self._test_verres()
        
    def _test_verres(self):
        v = [self.table.verres[6],self.table.verres[6],self.table.verres[7],self.table.verres[1],self.table.verres[0],self.table.verres[9],self.table.verres[8],self.table.verres[3],self.table.verres[2],self.table.verres[10],self.table.verres[11],self.table.verres[4],self.table.verres[5]]
        p = [verre["present"] for verre in v]
        
        arete_verres = [(v[1],v[2]),(v[1],v[5]),(v[2],v[5]),(v[2],v[6]),(v[3],v[4]),(v[3],v[7]),(v[3],v[8]),(v[4],v[8]),(v[5],v[6]),(v[5],v[9]),(v[5],v[10]),(v[6],v[7]),(v[6],v[10]),(v[7],v[8]),(v[7],v[11]),(v[8],v[11]),(v[8],v[12]),(v[9],v[10]),(v[11],v[12])]
        arete_grande_verres = [(v[1],v[6]),(v[1],v[9]),(v[2],v[7]),(v[2],v[10]),(v[2],v[3]),(v[3],v[6]),(v[3],v[11]),(v[4],v[7]),(v[4],v[12]),(v[6],v[9]),(v[6],v[11]),(v[7],v[10]),(v[7],v[12]),(v[10],v[11])]
        
        v.remove(v[0]) #position 0 inutilisée : juste pour le décalage d'index
        
        aux = [0] * 13

        #rajoute un verre virtuel là où ça ne change rien
        aux[5] = p[5]  or  (p[2]  and  p[6]  and  p[10]  and  (p[1]  or  p[9]))
        aux[8] = p[8]  or  (p[3]  and  p[7]  and  p[11]  and  (p[4]  or  p[2]))

        aux[2] = (p[6]  and  p[7]  and  (p[5]  and  p[1])  and  (p[3]  or  (p[8]  and  p[4])))  or  p[2]
        aux[3] = (p[6]  and  p[7]  and  ((p[5]  and  p[1])  or  p[2])  and  (p[8]  and  p[4]))  or  p[3]

        aux[10] = (p[6]  and  p[7]  and  (p[5]  and  p[9])  and  (p[11]  or  (p[8]  and  p[12])))  or  p[10]
        aux[11] = (p[6]  and  p[7]  and  ((p[5]  and  p[9])  or  p[10])  and  (p[8]  and  p[12]))  or  p[11]

        p[5] = aux[5]
        p[8] = aux[8]
        p[2] = aux[2]
        p[3] = aux[3]
        p[10] = aux[10]
        p[11] = aux[11]

        #supprime toutes les frontières intérieures
        gauche = [0] * 19
        droite = [0] * 19
        arete = [0] * 19

        gauche[1] = p[1] and (p[2] or p[6]) and p[5]
        droite[1] = p[1] and p[9] and p[5]
        arete[1] = p[1] and p[5] and not (droite[1] and gauche[1])

        droite[2] = p[2] and p[1] and p[5]
        gauche[2] = p[2] and (p[6] or p[10]) and p[5]
        arete[2] = p[2] and p[5] and not (droite[2] and gauche[2])

        gauche[3] = p[2] and p[7] and p[6]
        droite[3] = p[2] and (p[1] or p[5] or p[10]) and p[6]
        arete[3] = p[2] and p[6] and not (droite[3] and gauche[3])

        droite[5] = p[3] and p[6] and p[7]
        gauche[5] = p[3] and (p[4] or p[8] or p[11]) and p[7]
        arete[5] = p[3] and p[7] and not (droite[5] and gauche[5])

        gauche[6] = p[3] and p[4] and p[8]
        droite[6] = p[3] and (p[7] or p[11]) and p[8]
        arete[6] = p[3] and p[8] and not (droite[6] and gauche[6])

        droite[7] = p[4] and (p[3] or p[7]) and p[8]
        gauche[7] = p[4] and p[12] and p[8]
        arete[7] = p[4] and p[8] and not (droite[7] and gauche[7])

        gauche[8] = p[5] and (p[1] or p[2] ) and p[6] 
        droite[8] = p[5] and (p[9] or p[10]) and p[6] 
        arete[8] = p[5] and p[6] and not (droite[8] and gauche[8])

        droite[9] = p[5] and p[1] and p[9]
        gauche[9] = p[5] and (p[6] or p[10]) and p[9]
        arete[9] = p[5] and p[9] and not (droite[9] and gauche[9])

        droite[10] = p[5] and p[9] and p[10] 
        gauche[10] = p[5] and (p[6] or p[2]) and p[10] 
        arete[10] = p[5] and p[10] and not (droite[10] and gauche[10])

        gauche[11] = p[6] and p[7] and (p[2] or p[3])
        droite[11] = p[6] and p[7] and (p[10] or p[11])
        arete[11] = p[6] and p[7] and not (droite[11] and gauche[11])

        gauche[12] = p[6] and p[7] and p[10] 
        droite[12] = p[6] and (p[2] or p[5] or p[9]) and p[10] 
        arete[12] = p[6] and p[10] and not (droite[12] and gauche[12])

        gauche[13] = p[7] and (p[3] or p[4]) and p[8]
        droite[13] = p[7] and (p[11] or p[12]) and p[8]
        arete[13] = p[7] and p[8] and not (droite[13] and gauche[13])

        droite[14] = p[7] and p[6] and p[11] 
        gauche[14] = p[7] and (p[3] or p[8] or p[12]) and p[11] 
        arete[14] = p[7] and p[11] and not (droite[14] and gauche[14])

        droite[15] = p[8] and (p[3] or p[7]) and p[11]
        gauche[15] = p[8] and p[12] and p[11]
        arete[15] = p[8] and p[11] and not (droite[15] and gauche[15])

        gauche[16] = p[8] and p[4] and p[12]
        droite[16] = p[8] and (p[11] or p[7]) and p[12]
        arete[16] = p[8] and p[12] and not (droite[16] and gauche[16])

        # pour les grandes arrêtes éventuellement intérieures :
        arete_grande = [0] * 14
        arete_grande[0] = p[1] and (not (p[2] == p[5])) and p[6]
        arete_grande[2] = p[2] and p[6] and p[7] and not (p[3])
        arete_grande[3] = p[2] and (not (p[5] == p[6])) and p[10]
        arete_grande[5] = p[3] and p[7] and p[6] and not (p[2])
        arete_grande[6] = p[3] and (not (p[7] == p[8])) and p[11]
        arete_grande[7] = p[4] and (not (p[3] == p[8])) and p[7]
        arete_grande[9] = p[6] and (not (p[5] == p[10])) and p[9]
        arete_grande[10] = p[6] and p[7] and p[11] and not (p[10])
        arete_grande[11] = p[7] and p[6] and p[10] and not (p[11])
        arete_grande[12] = p[7] and (not (p[8] == p[11])) and p[12]

        # il reste 8 frontières, dont on calcule lactivation
        arete[0] = p[1] and p[2]
        arete[4] = p[3] and p[4]
        arete[17] = p[9] and p[10]
        arete[18] = p[11] and p[12]

        arete_grande[1] = p[1] and p[5] and p[9]
        arete_grande[8] = p[4] and p[8] and p[12]
        arete_grande[4] = p[6] and p[7] and p[2] and p[3] 
        arete_grande[13] = p[6] and p[7] and p[10] and p[11]
        
        ##################################
        aretes_bool = arete + arete_grande
        aretes_verres = arete_verres + arete_grande_verres
        polygones = []
        #rassemblage des aretes en polygones
        while len(aretes_verres)>0:
            #recherche d'un nouveau polygone
            if not aretes_bool[0]:
                del aretes_verres[0]
                del aretes_bool[0]
            else:
                #suppression des verres sur aretes (pour retenir les autres)
                try: v.remove(aretes_verres[0][0])
                except: pass#verre déjà supprimé
                try: v.remove(aretes_verres[0][1])
                except: pass#verre déjà supprimé
                
                polygones.append([aretes_verres[0][0]["position"],aretes_verres[0][1]["position"]])
                del aretes_verres[0]
                del aretes_bool[0]
                
                #completion du polygone
                k = 0
                while k < len(aretes_bool):
                    if aretes_bool[k]:
                        #suppression des verres sur aretes (pour retenir les autres)
                        try: v.remove(aretes_verres[k][0])
                        except: pass#verre déjà supprimé
                        try: v.remove(aretes_verres[k][1])
                        except: pass#verre déjà supprimé
                        
                        if aretes_verres[k][0]["position"] == polygones[-1][-1]:
                            polygones[-1].append(aretes_verres[k][1]["position"])
                            del aretes_verres[k]
                            del aretes_bool[k]
                            k = 0
                        elif aretes_verres[k][1]["position"] == polygones[-1][-1]:
                            polygones[-1].append(aretes_verres[k][0]["position"])
                            del aretes_verres[k]
                            del aretes_bool[k]
                            k = 0
                        else:
                            k += 1
                    else:
                        del aretes_verres[k]
                        del aretes_bool[k]
        
        for p in polygones:
            if len(p) > 2:
                #suppression des sommets plats
                p = self._lisser_chemin(p)
            if p[0] == p[-1]:
                #suppression du bouclage
                del p[-1]
                
            #création des polygones
            # -élargie les obstacles (prise en compte du rayon des verres)
            # -vérifie le sens de définition (antétrigonométrique) du polygone
            self.ajoute_obstacle_polygone(p,40,avecFusion=False)
            
        #ajout d'un cercle pour les verres seuls (hors polygones)
        for verre in [ver for ver in v if ver["present"]]:
            tout_seul = True
            for poly in polygones:
                if collisions.collisionPointPoly(verre["position"],poly):
                    tout_seul = False
                    break
            if tout_seul:
                self.ajoute_obstacle_cercle(verre["position"], self.config["rayon_verre"]-20, avecFusion=False)
        
        ########################## AFFICHAGE #########################"
        #clean affichage
        builtins.simulateur.clearEntity("opt_verres")
        for p in polygones:
            print(p)
            for i in range(1,len(p)):
                builtins.simulateur.drawLine(p[i-1].x,p[i-1].y,p[i].x,p[i].y,"red","opt_verres")
            builtins.simulateur.drawLine(p[len(p)-1].x,p[len(p)-1].y,p[0].x,p[0].y,"red","opt_verres")
            
        
        ##affichage des aretes
        #for k in range(len(arete)):
            #if arete[k]:
                #builtins.simulateur.drawLine(arete_verres[k][0]["position"].x,arete_verres[k][0]["position"].y,arete_verres[k][1]["position"].x,arete_verres[k][1]["position"].y,"blue","opt_verres")
        #for k in range(len(arete_grande)):
            #if arete_grande[k]:
                #builtins.simulateur.drawLine(arete_grande_verres[k][0]["position"].x,arete_grande_verres[k][0]["position"].y,arete_grande_verres[k][1]["position"].x,arete_grande_verres[k][1]["position"].y,"blue","opt_verres")
                
        #affichage des verres présents
        for verre in [ver for ver in v if ver["present"]]:
            builtins.simulateur.drawPoint(verre["position"].x,verre["position"].y,"blue","opt_verres")
        
    def charge_obstacles(self, avec_verres_entrees=True):
        ##ajout des obstacles vus par les capteurs et la balise
        #for obstacle in self.table.obstacles():
            #self.ajoute_obstacle_cercle(obstacle.position, obstacle.rayon)
            
        #ajout des obstacles vus par les capteurs (seulement)
        for obstacle in self.table.obstacles_capteurs:
            self.ajoute_obstacle_cercle(obstacle.position, obstacle.rayon)
            
        #ajout des verres encore présents sur la table
        self._ajoute_verres(avec_verres_entrees)
    
    
    ####################### PRÉPARATION DE L'ENVIRONNEMENT ET CALCUL DE TRAJET ########################
    
    def prepare_environnement_pour_a_star(self):
        """
        Prépare l'environnement nécessaire aux calculs effectués par l'algorithme de recherche de chemin A*. 
        Cela permet d'effectuer plusieurs recherches de chemin d'affilée sans avoir à recharger les obstacles.
        """
        haut_gauche = int(-self.config["table_x"]/2), int(self.config["table_y"])
        bas_droite = int(self.config["table_x"]/2), int(0)
        self.cercles_astar = [cercle for nuage in self.environnement_complet.nuages_de_cercles for cercle in nuage]
        self.graphe_table = aStar.AStar.creer_graphe(haut_gauche, bas_droite, self.cercles_astar)
        
    def cherche_chemin_avec_a_star(self, depart, arrivee):
        """
        Renvoi un chemin aux arêtes non lissées utilisé pour un calcul rapide de distance (inexploitable pour les scripts). 
        Prend en entrée deux Points depart et arrivee. 
        La sortie est une liste de points à suivre (ne contient pas le point de départ). 
        Une exception est levée si le point d'arrivée n'est pas accessible. 
        """
            
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas dans la table !")
            raise ExceptionArriveeHorsTable
        for obstacle in self.cercles_astar:
            if obstacle.contient(arrivee):
                self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas accessible !")
                raise ExceptionArriveeDansObstacle
            
        #recherche de chemin
        if not hasattr(self, 'graphe_table'):
            self.log.critical("Il faut appeler prepare_environnement_pour_a_star() avant cherche_chemin_avec_a_star() !")
            raise ExceptionEnvironnementNonPrepare
        
        #return aStar.AStar.plus_court_chemin(depart, arrivee, self.graphe_table)
        try:
            cheminAstar = aStar.AStar.plus_court_chemin(depart, arrivee, self.graphe_table)
            #lissage et suppression du point de départ
            return self._lisser_chemin(cheminAstar)[1:]
        except aStar.ExceptionAucunCheminAstar as e:
            raise ExceptionAucunChemin
        
    def prepare_environnement_pour_visilibity(self):
        """
        Sauvegarde l'environnement nécessaire aux calculs effectués par Visilibity. 
        Cela permet d'effectuer plusieurs recherches de chemin d'affilée sans avoir à recharger les obstacles.
        """
        
        if not self.valide:
            # l'environnement n'est pas adapté à une recherche de chemin par visilibity
            self.prepare_environnement_pour_a_star()
            return None
        
        # Création de l'environnement, le polygone des bords en premier, ceux des obstacles après (fixes et mobiles)
        self.environnement_visilibity = vis.Environment([self.bords]+self.environnement_complet.polygones)
        
        # Vérification de la validité de l'environnement : polygones non croisés et définis dans le sens des aiguilles d'une montre.
        if not self.environnement_visilibity.is_valid(RechercheChemin.tolerance):
            self.log.critical("Des obstacles invalides ont été trouvés. Ils sont remplacés par leurs cercles contenant.")
            
            for k in range(len(self.environnement_complet.polygones)):
                #détection du/des polygones défectueux
                if self.environnement_complet.polygones[k].area() >= 0 or not self.environnement_complet.polygones[k].is_simple(RechercheChemin.tolerance):
                    #environnement de secours : on remplace le polygone par son cercle contenant
                    self.environnement_complet.polygones[k] = Environnement._polygone_du_cercle(Environnement._cercle_contenant_nuage(self.environnement_complet.nuages_de_cercles[k]))
                    troncPolygon = self._recouper_aux_bords_table(self.environnement_complet.polygones[k], self.environnement_complet.nuages_de_cercles[k], self.environnement_complet)
                    if troncPolygon is None:
                        #le polygone n'est pas dans la table : on le retire
                        del self.environnement_complet.polygones[k]
                        del self.environnement_complet.nuages_de_cercles[k]
                    else:
                        #on enregistre le nouveau polygone tronqué
                        self.environnement_complet.polygones[k] = troncPolygon
                        
                    self.log.warning("L'obstacle "+str(k)+" a été remplacé.")
                    
            #environnement de secours en cas d'obstacle invalide
            self.environnement_visilibity = vis.Environment([self.bords]+self.environnement_complet.polygones)
            #validation du nouvel environnement
            self.environnement_visilibity.is_valid(RechercheChemin.tolerance)
      
    def cherche_chemin_avec_visilibity(self, depart, arrivee, relanceProblemeDepart=False, relanceProblemeArrivee=False):
        """
        Renvoi le chemin pour aller de depart à arrivee sous forme d'une liste. Le point de départ est exclu. 
        Une exception est levée si le point d'arrivée n'est pas accessible. 
        En cas de problème avec les obstacles (ex: erreur lors d'une fusion de polygones), des calculs plus grossiers sont effectués de facon à toujours renvoyer un chemin.
        """
        
        if not self.valide:
            self.log.critical("L'environnement n'est pas adapté à visilibity : recherche de chemin avec A*")
            return self.cherche_chemin_avec_a_star(depart,arrivee)
            
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas dans la table !")
            raise ExceptionArriveeHorsTable
        for obstacle in self.environnement_complet.polygones:
            # Le point de départ est dans un obstacle
            if collisions.collisionPointPoly(depart,obstacle):
                if not relanceProblemeDepart:
                    self.log.warning("Le point de départ "+str(depart)+" est dans un obstacle !")
                    for nouveauDepart in [point.Point(depart.x + self.config["disque_tolerance_consigne"]*math.cos(2*math.pi*i/6), depart.y + self.config["disque_tolerance_consigne"]*math.sin(2*math.pi*i/6)) for i in range(6)]:
                        try:
                            autreChemin = self.cherche_chemin_avec_visilibity(nouveauDepart, arrivee, relanceProblemeDepart=True)
                            self.log.warning("Un point de départ de substitution a été trouvé : "+str(nouveauDepart)+".")
                            return autreChemin
                        except ExceptionDepartDansObstacle:
                            pass
                else:
                    raise ExceptionDepartDansObstacle
                # Aucun point de départ de substitution n'a pu être trouvé. On tente quand même...
            
            # Le point d'arrivée est dans un obstacle
            if collisions.collisionPointPoly(arrivee,obstacle):
                if not relanceProblemeArrivee:
                    self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas accessible !")
                    for nouvelleArrivee in [point.Point(arrivee.x + self.config["disque_tolerance_consigne"]*math.cos(2*math.pi*i/6), arrivee.y + self.config["disque_tolerance_consigne"]*math.sin(2*math.pi*i/6)) for i in range(6)]:
                        try:
                            autreChemin = self.cherche_chemin_avec_visilibity(depart, nouvelleArrivee, relanceProblemeArrivee=True)
                            self.log.warning("Un point d'arrivée de substitution a été trouvé : "+str(nouvelleArrivee)+".")
                            return autreChemin
                        except ExceptionArriveeDansObstacle:
                            pass
                # Aucun point d'arrivé de substitution n'a pu être trouvé : le chemin est impossible.
                raise ExceptionArriveeDansObstacle
            
        #conversion en type vis.PointVisibility
        departVis = vis.Point(depart.x,depart.y)
        arriveeVis = vis.Point(arrivee.x, arrivee.y)
        
        #recherche de chemin
        if not hasattr(self, 'environnement_visilibity'):
            self.log.critical("Il faut appeler prepare_environnement_pour_visilibity() avant cherche_chemin_avec_visilibity() !")
            raise ExceptionEnvironnementNonPrepare
        cheminVis = self.environnement_visilibity.shortest_path(departVis, arriveeVis, RechercheChemin.tolerance)
        
        #conversion en type point.Point, exclusion du point de départ cheminVis[0], et évacuation des points sur les bords.
        chemin = [point.Point(cheminVis[i].x,cheminVis[i].y) for i in range(1,cheminVis.size()) if self._est_dans_table(cheminVis[i])]
        if len(chemin) == cheminVis.size()-1:
            return self._lisser_chemin([depart]+chemin)[1:]
        else:
            #un des points était en fait sur le bord : le chemin est impossible.
            self.log.critical("Aucun chemin ne convient pour aller de "+str(depart)+" à "+str(arrivee)+" !")
            raise ExceptionAucunChemin
          
          
class ExceptionArriveeHorsTable(Exception):
    """
    Exception levée lorsque le point d'arrivée n'est pas dans la table.
    """
    def __str__(self):
        return "Le point d'arrivée n'est pas dans la table !"

class ExceptionArriveeDansObstacle(Exception):
    """
    Exception levée lorsque le point d'arrivée se situe dans un obstacle.
    """
    def __str__(self):
        return "Le point d'arrivée est dans un obstacle !"
        
class ExceptionDepartDansObstacle(Exception):
    """
    Exception levée lorsque le point de départ se situe dans un obstacle.
    """
    def __str__(self):
        return "Le point de départ est dans un obstacle !"

class ExceptionEnvironnementNonPrepare(Exception):
    """
    Exception levée lorsqu'une méthode de recherche de chemin est appellée avant de préparer l'environnement.
    """
    def __str__(self):
        return "L'environnement de recherche de chemin n'a pas été chargé !"

class ExceptionAucunChemin(Exception):
    """
    Exception levée lorsqu'aucun chemin ne peut relier le départ à l'arrivée.
    """
    def __str__(self):
        return "Aucun chemin possible !"
        
class RechercheCheminSimulation(RechercheChemin):

    def __init__(self, simulateur, table, config, log):
        self.simulateur = simulateur
        super().__init__(table, config, log)
            
    def prepare_environnement_pour_visilibity(self):
        RechercheChemin.prepare_environnement_pour_visilibity(self)
        
        self.simulateur.clearEntity("rc_obst")
            
        for obstacle in RechercheChemin.get_obstacles(self):
            for i in range(1,obstacle.n()):
                self.simulateur.drawLine(obstacle[i-1].x,obstacle[i-1].y,obstacle[i].x,obstacle[i].y,"green","rc_obst")
            self.simulateur.drawLine(obstacle[obstacle.n()-1].x,obstacle[obstacle.n()-1].y,obstacle[0].x,obstacle[0].y,"green","rc_obst")
            
    def cherche_chemin_avec_a_star(self, depart, arrivee):
        chemin = RechercheChemin.cherche_chemin_avec_a_star(self, depart, arrivee)
         
        self.simulateur.clearEntity("rc_chemin")
        for p1,p2 in zip([depart]+chemin[:-1],chemin):
            self.simulateur.drawPoint(p1.x,p1.y,"red","rc_chemin")
            self.simulateur.drawLine(p1.x,p1.y,p2.x,p2.y,"red","rc_chemin")
        self.simulateur.drawPoint(chemin[-1].x,chemin[-1].y,"red","rc_chemin")
            
        return chemin
    
    def cherche_chemin_avec_visilibity(self, depart, arrivee, relanceProblemeDepart=False, relanceProblemeArrivee=False):
        chemin = RechercheChemin.cherche_chemin_avec_visilibity(self, depart, arrivee, relanceProblemeDepart, relanceProblemeArrivee)
        
        self.simulateur.clearEntity("rc_chemin")
        for p1,p2 in zip([depart]+chemin[:-1],chemin):
            self.simulateur.drawPoint(p1.x,p1.y,"red","rc_chemin")
            self.simulateur.drawLine(p1.x,p1.y,p2.x,p2.y,"red","rc_chemin")
        self.simulateur.drawPoint(chemin[-1].x,chemin[-1].y,"red","rc_chemin")
            
        return chemin