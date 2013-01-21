import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

try:
    import recherche_de_chemin.visilibity as vis
except:
    input("\n\nProblème avec la bibliothèque compilée _visilibity.so !\nConsultez le README dans src/recherche_de_chemin/visilibity/\n")
import math
import recherche_de_chemin.collisions as collisions

class Cercle:
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
    def copy(self):
        return Cercle(vis.Point(self.centre.x, self.centre.y), self.rayon)
        
class Environnement:
    
    def __init__(self):
        self.cercles = []
        self.polygones = []
        
        # côté des polygones qui représentent des cercles, en mm (petit : précision, grand : complexité moindre)
        self.cote_polygone = 100
        
    def copy(self):
        new = Environnement()
        new.cercles = list(map(lambda c: c.copy(), self.cercles))
        for poly in self.polygones:
            newPoly = []
            for k in range(poly.n()):
                newPoly.append(vis.Point(poly[k].x, poly[k].y))
            new.polygones.append(vis.Polygon(newPoly))
        #new.polygones = list(map(lambda poly: list(map(lambda point: vis.Point(point.x, point.y), poly)), self.polygones))
        return new
    
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
        
    #def _get_polygone_convexe(self,id):
        #"""
        #renvoi le polygone convexe minimal contenant l'obstacle
        #"""
        #polyConvexe = []
        #for k in range(self.polygones[id].n()):
            #polyConvexe.append(vis.Point(self.polygones[id][k].x, self.polygones[id][k].y))
        
        #def get_angle(a,o,b):
            #oa = vis.Point(a.x-o.x,a.y-o.y)
            #ob = vis.Point(b.x-o.x,b.y-o.y)
            #theta = math.atan2(ob.y,ob.x) - math.atan2(oa.y,oa.x)
            #if theta > math.pi :theta -= 2*math.pi
            #elif theta <= -math.pi :theta += 2*math.pi
            #return theta
            
        #def avancerSurPolygone(poly,position):
                #if position < len(poly)-1: return position + 1
                #else: return 0
        
        #def reculerSurPolygone(poly,position):
                #if position > 0: return position - 1
                #else: return len(poly)-1
                
        #o = 0
        #a = avancerSurPolygone(polyConvexe,o)
        #b = avancerSurPolygone(polyConvexe,a)
        #depart = False
        #termine = False
        #while not termine:
            #angle = get_angle(polyConvexe[o],polyConvexe[a],polyConvexe[b])
            #if angle <= 0:
                ##concavité
                #deleted = a
                #a = o
                #o = reculerSurPolygone(polyConvexe,o)
                #if o >= deleted: o-= 1
                #if a >= deleted: a-= 1
                #if b >= deleted: b-= 1
                #del polyConvexe[deleted]
            #else:
                #o = a
                #a = b
                #b = avancerSurPolygone(polyConvexe,b)
            #if o == 2:
                #depart = True
            #if depart and o == 0:
                #termine = True
        #return vis.Polygon(polyConvexe)
    
        
    def _cercle_circonscrit_du_polygone(self,polygone):
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
        a = vis.Point(parcourt["minX"],parcourt["maxY"])
        b = vis.Point(parcourt["maxX"],parcourt["maxY"])
        c = vis.Point(parcourt["maxX"],parcourt["minY"])
        d = vis.Point(parcourt["minX"],parcourt["minY"])
        return self._cercle_circonscrit_du_rectangle([a,b,c,d])
        
        """
        #méthode du centre au milieu du plus long segment (cercle plus précis, méthode plus lente)
        parcourt = {"lgr":0}
        for i in range(polygone.n()):
            for j in range(i,polygone.n()):
                lgr = math.sqrt((polygone[i].x - polygone[j].x)**2 + (polygone[i].y - polygone[j].y)**2)
                if lgr > parcourt["lgr"]:
                    parcourt["lgr"] = lgr
                    parcourt["point1"] = polygone[i]
                    parcourt["point2"] = polygone[j]
        centre = vis.Point((parcourt["point1"].x + parcourt["point2"].x)/2,(parcourt["point1"].y + parcourt["point2"].y)/2)
        parcourt["rayon"] = 0
        for i in range(polygone.n()):
            ray = math.sqrt((polygone[i].x - centre.x)**2 + (polygone[i].y - centre.y)**2)
            if ray > parcourt["rayon"]:
                parcourt["rayon"] = ray
        rayon = parcourt["rayon"]
        return Cercle(centre,rayon)
        """
        
        """
        #méthode de l'angle le plus aigu (cercle minimal, méthode la plus lente, et plus compliquée)
        #parcourir le polygone convexe pour obtenir l'angle le plus aigu avec un coté arbitraire, et faire un cercle par 3 points
        """
        
    def ajoute_cercle(self, cercle):
        self.cercles.append(cercle)
        self.polygones.append(self._polygone_du_cercle(cercle))
    
    def ajoute_rectangle(self, rectangle):
        self.polygones.append(rectangle)
        self.cercles.append(self._cercle_circonscrit_du_rectangle(rectangle))
        
    def ajoute_polygone(self, listePoints):
        polygone = vis.Polygon(list(map(lambda p: vis.Point(p.x,p.y), listePoints)))
        self.polygones.append(polygone)
        self.cercles.append(self._cercle_circonscrit_du_polygone(polygone))
        
    
class RechercheChemin:
    
    def __init__(self,table,config,log):
        
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        # tolerance de précision (différent de 0.0)
        self.tolerance = 0.001
        
        # bords de la carte
        self.bords = vis.Polygon([vis.Point(-self.config["table_x"]/2,0), vis.Point(self.config["table_x"]/2,0), vis.Point(self.config["table_x"]/2,self.config["table_y"]), vis.Point(-self.config["table_x"]/2,self.config["table_y"])])
        
        # environnement initial : obstacles fixes sur la carte
        self.environnement_initial = Environnement()
        # Définition des polygones des obstacles fixes. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(100, 300),vis.Point(100, 500),vis.Point(150, 500),vis.Point(150, 300)]))
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(0, 875),vis.Point(0, 1125),vis.Point(775, 1125),vis.Point(775, 875)]))
        self.environnement_initial.ajoute_rectangle(vis.Polygon([vis.Point(-775, 875),vis.Point(-775, 1125),vis.Point(-525, 1125),vis.Point(-525, 875)]))
        
        # environnement dynamique : liste des obstacles mobiles qui sont mis à jour régulièrement
        self.environnement_complet = self.environnement_initial.copy()
        
        
    ### Pour l'environnement dynamique #########
    def ajoute_obstacle_cercle(self, centre, rayon):
        cercle = Cercle(centre,rayon)
        self.environnement_complet.ajoute_cercle(cercle)
        self._recouper_aux_bords_table()
        self._fusionner_avec_obstacles_en_contact()
            
    def retirer_obstacles_dynamiques(self):
        #on retourne à l'environnement initial, en évitant de le modifier
        self.environnement_complet = self.environnement_initial.copy()
    ############################################
    
    def _recouper_aux_bords_table(self):
        #TODO SUPPRIMER : WATCHDOG
        
        #alias pour la clarté. Les polygones NE SONT PAS dupliqués (pointeurs)
        poly1 = self.environnement_complet.polygones[-1]
        poly2 = self.bords
        #élection d'un point du poly1 qui ne sort pas de la table
        a1 = None
        for k in range(poly1.n()):
            if collisions.collisionPointPoly(poly1[k],poly2):
                a1 = k
                break
        if not type(a1) == int:
            #Le polygone n'a aucun sommet dans la table. On considère qu'on peut l'ignorer.
            self.log.warning("L'obstacle n'est pas dans la table.")
            del self.environnement_complet.polygones[-1]
            del self.environnement_complet.cercles[-1]
            return None
        
        def avancerSurPolygone(poly,position):
            if poly == self.bords:
                if position > 0: return position - 1
                else: return poly.n()-1
            else:
                if position < poly.n()-1: return position + 1
                else: return 0
                
        #création de l'obstacle recoupé
        troncateObstacle = []
        #on va considérer le segment allant jusqu'au point voisin de a1
        b1 = avancerSurPolygone(poly1,a1)
        WATCHDOG = 0
        auMoinsUneCollision = False
        conditionBouclage = True
        def ajouterTroncateObstacle(point):
            nonlocal conditionBouclage
            try:
                if point == troncateObstacle[0]:
                    conditionBouclage = False
                else:
                    if conditionBouclage:
                        troncateObstacle.append(point)
            except:
                troncateObstacle.append(point)
        ajouterTroncateObstacle(poly1[a1])
        while conditionBouclage and WATCHDOG < 100:
            WATCHDOG += 1
            #print(poly1[a1],poly1[b1])#@
            #input("parcourir ce segment !")#@
            #tests de collision du segment [a1,b1] de poly1 avec les segments de poly2
            collision = False
            pointCollision = None
            for a2 in range(poly2.n()):
                b2 = avancerSurPolygone(poly2,a2)
                pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                if pCollision:
                    #self.log.critical("collision à "+str(pCollision[1]))#@
                    pointCollision = pCollision[1]
                    collision = True
                    auMoinsUneCollision = True
                    break
            if collision:
                ajouterTroncateObstacle(pointCollision)
                #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                sopalin = poly1
                poly1 = poly2
                poly2 = sopalin
                #toujours dans le sens horaire : à partir du plus petit indice
                if poly1 == self.bords:
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = poly1.n()-1
                    else: a1 = min(a2,b2)
                else:
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                    else: a1 = max(a2,b2)
                
                #------------------------
                continueSurSegment = True
                while continueSurSegment:
                    #print("collision sur du "+str(poly2.n())+" sur "+str(poly1.n())+" à "+str(pointCollision))#@
                    #input("voir les autres collisions sur le meme segment !")#@
                    collision = False
                    for a2 in range(poly2.n()):
                        b2 = avancerSurPolygone(poly2,a2)
                        pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                        if pCollision:
                            #self.log.warning("autre collision à "+str(pCollision[1]))#@
                            pointCollision = pCollision[1]
                            collision = True
                            break
                    if collision:
                        ajouterTroncateObstacle(pointCollision)
                        #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                        sopalin = poly1
                        poly1 = poly2
                        poly2 = sopalin
                        #toujours dans le sens horaire : à partir du plus petit indice
                        if poly1 == self.bords:
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = poly1.n()-1
                            else: a1 = min(a2,b2)
                        else:
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                            else: a1 = max(a2,b2)
                    else:
                        continueSurSegment = False
                        ajouterTroncateObstacle(poly1[a1])
                        #parcourt du segment suivant sur l'ex poly2
                        b1 = avancerSurPolygone(poly1,a1)
                #------------------------
                
            else :
                #self.log.debug("ajout de "+str(poly1[a1])+" au polygone")#@
                #parcourt du segment suivant
                a1 = b1
                b1 = avancerSurPolygone(poly1,a1)
                ajouterTroncateObstacle(poly1[a1])
        if WATCHDOG == 100:
            self.log.critical("récursion non terminale pour le polygone tronqué !")
            raise Exception
            
        if auMoinsUneCollision:
            self.log.warning("cet obstacle rentre en collision avec les bords de la table. Il a été tronqué.")
            #remplacement de l'obstacle par l'obstacle tronqué
            #print("########")#@
            for i in range(len(troncateObstacle)):
                #print(troncateObstacle[i])#@
                if troncateObstacle[i].x < -self.config["table_x"]/2+self.tolerance:
                    troncateObstacle[i].x = -self.config["table_x"]/2+2*self.tolerance
                elif troncateObstacle[i].x > self.config["table_x"]/2-self.tolerance:
                    troncateObstacle[i].x = self.config["table_x"]/2-2*self.tolerance
                if troncateObstacle[i].y < self.tolerance:
                    troncateObstacle[i].y = 2*self.tolerance
                elif troncateObstacle[i].y > self.config["table_y"]-self.tolerance:
                    troncateObstacle[i].y = self.config["table_y"]-2*self.tolerance
                
            troncPolygon = vis.Polygon(troncateObstacle)
            self.environnement_complet.polygones[-1] = troncPolygon
            self.environnement_complet.cercles[-1] = self.environnement_complet._cercle_circonscrit_du_polygone(troncPolygon)
        else:
            self.log.warning("cet obstacle ne rentre pas en collision avec les bords de la table.")
        
        
    def _fusionner_avec_obstacles_en_contact(self):
        #TODO SUPPRIMER WATCHDOG
        
        #teste tous les polygones avec le dernier ajouté
        for i in range(len(self.environnement_complet.polygones)-1,0,-1):
            #test rapide de collision entre les cercles circonscrits aux 2 polygones
            if not collisions.collision_2_cercles(self.environnement_complet.cercles[i],self.environnement_complet.cercles[-1]):
                self.log.warning("pas de collision cercle")
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
            
            def avancerSurPolygone(poly,position):
                if position < poly.n()-1: return position + 1
                else: return 0
                    
            #création de l'obstacle de merge
            mergeObstacle = []
            #on va considérer le segment allant jusqu'au point voisin de a1
            b1 = avancerSurPolygone(poly1,a1)
            WATCHDOG = 0
            auMoinsUneCollision = False
            conditionBouclage = True
            def ajouterMergeObstacle(point):
                nonlocal conditionBouclage
                try:
                    if point == mergeObstacle[0]:
                        conditionBouclage = False
                    else:
                        if conditionBouclage:
                            mergeObstacle.append(point)
                except:
                    mergeObstacle.append(point)
            while conditionBouclage and WATCHDOG < 100:
                WATCHDOG += 1
                #tests de collision du segment [a1,b1] de poly1 avec les segments de poly2
                collision = False
                pointCollision = None
                for a2 in range(poly2.n()):
                    b2 = avancerSurPolygone(poly2,a2)
                    pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                    if pCollision:
                        pointCollision = pCollision[1]
                        collision = True
                        auMoinsUneCollision = True
                        break
                if collision:
                    ajouterMergeObstacle(pointCollision)
                    #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                    sopalin = poly1
                    poly1 = poly2
                    poly2 = sopalin
                    #toujours dans le sens horaire : vers les indices croissants
                    if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                    else: a1 = max(a2,b2)
                    
                    #------------------------
                    continueSurSegment = True
                    while continueSurSegment:
                        #print("collision sur du "+str(poly2.n())+" sur "+str(poly1.n())+" à "+str(pointCollision))#@
                        #input("voir les autres collisions sur le meme segment !")#@
                        collision = False
                        for a2 in range(poly2.n()):
                            b2 = avancerSurPolygone(poly2,a2)
                            pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                            if pCollision:
                                #self.log.warning("autre collision à "+str(pCollision[1]))#@
                                pointCollision = pCollision[1]
                                collision = True
                                break
                        if collision:
                            ajouterMergeObstacle(pointCollision)
                            #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                            sopalin = poly1
                            poly1 = poly2
                            poly2 = sopalin
                            #toujours dans le sens horaire : à partir du plus petit indice
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                            else: a1 = max(a2,b2)
                        else:
                            continueSurSegment = False
                            ajouterMergeObstacle(poly1[a1])
                            #parcourt du segment suivant sur l'ex poly2
                            b1 = avancerSurPolygone(poly1,a1)
                    #------------------------
                else :
                    #parcourt du segment suivant
                    a1 = b1
                    b1 = avancerSurPolygone(poly1,a1)
                    ajouterMergeObstacle(poly1[a1])
            if WATCHDOG == 100:
                self.log.critical("récursion non terminale pour le polygone de fusion !")
                raise Exception
                
            if auMoinsUneCollision:
                self.log.warning("cet obstacle rentre en collision avec un autre obstacle. Ils ont été fusionnés.")
                #remplacement du premier obstacle par l'obstacle de fusion 
                mergePolygon = vis.Polygon(mergeObstacle)
                self.environnement_complet.polygones[-1] = mergePolygon
                self.environnement_complet.cercles[-1] = self.environnement_complet._cercle_circonscrit_du_polygone(mergePolygon)
                #suppression du deuxième obstacle
                del self.environnement_complet.polygones[i]
                del self.environnement_complet.cercles[i]
            else:
                self.log.warning("cet obstacle ne rentre pas en collision avec un autre obstacle.")
                    
        
    def get_obstacles(self):
        return (self.environnement_complet.polygones)
        
    def get_cercles_obstacles(self):
        return list(map(lambda cercle: self.environnement_complet._polygone_du_cercle(cercle), self.environnement_complet.cercles))
        
    def get_chemin(self,depart,arrivee):
        
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée n'est pas dans la table !")
            raise Exception
        for obstacle in self.environnement_complet.polygones:
            if collisions.collisionPointPoly(arrivee,obstacle):
                self.log.critical("Le point d'arrivée n'est pas accessible !")
                raise Exception
            
        #conversion en type vis.PointVisibility
        departVis = vis.Point(depart.x,depart.y)
        arriveeVis = vis.Point(arrivee.x, arrivee.y)
        
        # Création de l'environnement, le polygone des bords en premier, ceux des obstacles après (fixes et mobiles)
        env = vis.Environment([self.bords]+self.environnement_complet.polygones)
        
        # Vérification de la validité de l'environnement : polygones non croisés et définis dans le sens des aiguilles d'une montre.
        if not env.is_valid(self.tolerance):
            raise Exception
            
        #recherche de chemin
        cheminVis = env.shortest_path(departVis, arriveeVis, self.tolerance)
        
        #conversion en type vis.Point
        chemin = []
        for i in range(cheminVis.size()):
            chemin.append(vis.Point(cheminVis[i].x,cheminVis[i].y))
        return chemin