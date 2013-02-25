import os,sys
import math

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#bibliothèque compilée de recherche de chemin
try:
    import recherche_de_chemin.aStar as aStar
except:
    input("\n\nproblème d'importation de la bibliothèque de recherche de chemin aStar !\n")

try:
    import recherche_de_chemin.visilibity as vis
except:
    input("\n\nProblème avec la bibliothèque compilée _visilibity.so !\nConsultez le README dans src/recherche_de_chemin/visilibity/\n")

#fonctions auxiliaires pour les calculs géométriques
import recherche_de_chemin.collisions as collisions
import recherche_de_chemin.fonctions_auxiliaires_fusion as fus
import recherche_de_chemin.fonctions_auxiliaires_elargissement as enlarge

from outils_maths.cercle import Cercle
#from outils_maths.point import Point
from recherche_de_chemin.visilibity import Point


class Environnement:
    # côté des polygones qui représentent des cercles, en mm (petit : précision, grand : complexité moindre)
    cote_polygone = 500
    
    def __init__(self):
        self.cercles = []
        self.polygones = []
        
    def copy(self):
        """
        Clone un objet environnement pour éviter d'avoir deux pointeurs vers la même instance. 
        Tous ses attributs doivent être clonés, de manière récursive. 
        """
        new = Environnement()
        new.cercles = list(map(lambda c: c.copy(), self.cercles))
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
        
    def ajoute_cercle(self, cercle):
        """
        Ajoute un obstacle circulaire à l'environnement. 
        L'obstacle proprement dit est le polygone. Le cercle stocké permet d'optimiser les calculs de collisions.
        """
        self.cercles.append(cercle)
        self.polygones.append(Environnement._polygone_du_cercle(cercle))
    
    def ajoute_rectangle(self, polygoneVisilibity):
        """
        Ajoute un obstacle rectangulaire à l'environnement, sous forme d'un polygone (liste de points). 
        Le cercle stocké permet d'optimiser les calculs de collisions. 
        """
        self.polygones.append(polygoneVisilibity)
        self.cercles.append(Environnement._cercle_circonscrit_du_rectangle(polygoneVisilibity))
        
    def ajoute_polygone(self, polygoneVisilibity):
        """
        Ajoute un obstacle polygonal à l'environnement, sous forme d'un polygone (liste de points). 
        Le cercle stocké permet d'optimiser les calculs de collisions. 
        """
        self.polygones.append(polygoneVisilibity)
        self.cercles.append(Environnement._cercle_circonscrit_du_polygone(polygoneVisilibity))
        
class RechercheChemin:
    """
    Classe implémentant une recherche de chemin sur la table. 
    Elle utilise la bibliothèque compilée _visilibity.so, et s'occupe d'ajouter correctement les obstacles sur la table. 
    Elle veille en particulier à fusionner les obstacles adjacents. 
    Les obstacles initiaux de la table sont déclarés dans son constructeur. 
    """
    
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
        
    def _ajoute_obstacle_initial_cercle(self, centre, rayon):
        """
        Ajoute un obstacle circulaire à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        cercleObstacle = enlarge.elargit_cercle(Cercle(centre,rayon),self.rayonPropre)
        self.environnement_initial.ajoute_cercle(cercleObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_initial)
        self.environnement_initial.polygones[-1] = troncPolygon
        self.environnement_initial.cercles[-1] = cercleObstacle
    
    def _ajoute_obstacle_initial_rectangle(self, rectangle):
        """
        Ajoute un obstacle rectangulaire à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), rectangle)))
        rectangleObstacle = enlarge.elargit_rectangle(polygoneVisilibity, self.rayonPropre)
        self.environnement_initial.ajoute_rectangle(rectangleObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_initial)
        self.environnement_initial.polygones[-1] = troncPolygon
        self.environnement_initial.cercles[-1] = Environnement._cercle_circonscrit_du_polygone(troncPolygon)
        
    def _ajoute_obstacle_initial_polygone(self, polygone):
        """
        Ajoute un obstacle polygonal à l'environnement initial. 
        Cette méthode recoupe ensuite le dernier polygone de l'environnement (indice -1) s'il sort de la table.
        """
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), polygone)))
        polygoneObstacle = enlarge.elargit_polygone(polygoneVisilibity, self.rayonPropre, Environnement.cote_polygone)
        self.environnement_initial.ajoute_polygone(polygoneObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_initial)
        self.environnement_initial.polygones[-1] = troncPolygon
        self.environnement_initial.cercles[-1] = Environnement._cercle_circonscrit_du_polygone(troncPolygon)
        
    def _recouper_aux_bords_table(self,id,environnement):
        """
        Cette méthode recoupe le id-ème polygone de l'environnement passé en paramètre s'il sort de la table.
        """
        #les obstacles une fois tronqués devront être distants de eps des bords
        eps = 1
        
        #test rapide de collision du polygone avec les bords de la table, via son cercle circonscrit
        cx = environnement.cercles[id].centre.x
        cy = environnement.cercles[id].centre.y
        cr = environnement.cercles[id].rayon
        if cx+cr < self.config["table_x"]/2-eps and cx-cr > -self.config["table_x"]/2+eps and cy+cr < self.config["table_y"]-eps and cy-cr > eps:
            #self.log.warning("le cercle de l'obstacle "+str(i)+" ne rentre pas en collision avec les bords.")#@
            return environnement.polygones[id]
        
        #alias pour la clarté. Les polygones NE SONT PAS dupliqués (pointeurs)
        poly1 = environnement.polygones[id]
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
        #le watchdog lève une exception en cas de récursivité non terminale. Meuh non, ca n'arrive pas (plus)...
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
            self.log.critical("récursion non terminale pour le polygone tronqué !")
            raise Exception
        
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
        troncPolygon = vis.Polygon(troncateObstacle)
        return troncPolygon
        
    def _fusionner_avec_obstacles_en_contact(self,sEstDejaRetrouveEnferme=False):
        #teste le dernier polygone ajouté avec tous les autres, en les parcourant par id décroissant
        for i in range(len(self.environnement_complet.polygones)-2,-1,-1):
            #self.log.debug("--> "+str(i))#@
            #test rapide de collision entre les cercles circonscrits aux 2 polygones
            if not collisions.collision_2_cercles(self.environnement_complet.cercles[i],self.environnement_complet.cercles[-1]):
                #self.log.warning("pas de collision avec le cercle de l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+".")#@
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
                self.log.critical("récursion non terminale pour le polygone de fusion !")
                raise Exception
                
            if auMoinsUneCollision:
                #self.log.warning("cet obstacle rentre en collision avec l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+". Ils ont été fusionnés.")
                #remplacement du premier obstacle par l'obstacle de fusion 
                mergePolygon = vis.Polygon(mergeObstacle)
                
                #test si le polygone est bien déclaré dans le sens horaire
                if mergePolygon.area() < 0:
                    #polygone ok, on le place dans l'environnement
                    self.environnement_complet.polygones[-1] = mergePolygon
                    self.environnement_complet.cercles[-1] = Environnement._cercle_circonscrit_du_polygone(mergePolygon)
                    #suppression du deuxième obstacle
                    del self.environnement_complet.polygones[i]
                    del self.environnement_complet.cercles[i]
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
                #self.log.warning("cet obstacle ne rentre pas en collision avec l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+".")
                
    def ajoute_obstacle_cercle(self, centre, rayon):
        """
        Ajout un obstacle circulaire sur la table.
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        cercleObstacle = enlarge.elargit_cercle(Cercle(centre,rayon),self.rayonPropre)
        self.environnement_complet.ajoute_cercle(cercleObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_complet)
        if troncPolygon:
            self.environnement_complet.polygones[-1] = troncPolygon
            self.environnement_complet.cercles[-1] = cercleObstacle
        self._fusionner_avec_obstacles_en_contact()
        
    def ajoute_obstacle_polygone(self, polygone):
        """
        Ajout un obstacle polygonal sur la table (liste de points). 
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), polygone)))
        polygoneObstacle = enlarge.elargit_polygone(polygoneVisilibity, self.rayonPropre, Environnement.cote_polygone)
        self.environnement_complet.ajoute_polygone(polygoneObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_complet)
        self.environnement_complet.polygones[-1] = troncPolygon
        self.environnement_complet.cercles[-1] = Environnement._cercle_circonscrit_du_polygone(troncPolygon)
        self._fusionner_avec_obstacles_en_contact()
        
    def ajoute_obstacle_rectangle(self, rectangle):
        """
        Ajout un obstacle rectangulaire sur la table (liste de points). 
        Idem que ajoute_obstacle_polygone() mais avec une optimisation du calcul du cercle circonscrit. 
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        polygoneVisilibity = vis.Polygon(list(map(lambda p: Point(p.x,p.y), rectangle)))
        rectangleObstacle = enlarge.elargit_rectangle(polygoneVisilibity, self.rayonPropre)
        self.environnement_complet.ajoute_rectangle(rectangleObstacle)
        troncPolygon = self._recouper_aux_bords_table(-1,self.environnement_complet)
        self.environnement_complet.polygones[-1] = troncPolygon
        self.environnement_complet.cercles[-1] = Environnement._cercle_circonscrit_du_polygone(troncPolygon)
        self._fusionner_avec_obstacles_en_contact()
            
    def retirer_obstacles_dynamiques(self):
        """
        Retire les obstacles dynamiques et retourne à l'environnement initial
        """
        #on retourne à l'environnement initial, en évitant de le modifier
        self.environnement_complet = self.environnement_initial.copy()
        
    def preparer_environnement(self):
        haut_gauche = int(-self.config["table_x"]/2), int(self.config["table_y"])
        bas_droite = int(self.config["table_x"]/2), int(0)
        self.graphe_table = aStar.AStar.creer_graphe(haut_gauche, bas_droite, self.environnement_complet.cercles)
        
    def get_obstacles(self):
        """
        Renvoi la liste des polygones obstacles (initiaux et dynamiques)
        """
        return (self.environnement_complet.polygones)
        
    def get_cercles_obstacles(self):
        """
        Renvoi la liste des cercles contenant les obstacles (initiaux et dynamiques)
        """
        return list(map(lambda cercle: Environnement._polygone_du_cercle(cercle), self.environnement_complet.cercles))
    
    def get_chemin(self,depart,arrivee):
        """
        Renvoi le chemin pour aller de depart à arrivee sous forme d'une liste. Le point de départ est exclu. 
        Une exception est levée si le point d'arrivée n'est pas accessible. 
        En cas de problème avec les obstacles (ex: erreur lors d'une fusion de polygones), des calculs plus grossiers sont effectués de facon à toujours renvoyer un chemin.
        """
        
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée n'est pas dans la table !")
            raise Exception
        for obstacle in self.environnement_complet.polygones:
            if collisions.collisionPointPoly(arrivee,obstacle):
                self.log.critical("Le point d'arrivée n'est pas accessible !")
                raise Exception
            
        #recherche de chemin
        chemin = aStar.AStar.plus_court_chemin(depart, arrivee, self.graphe_table)
        return chemin