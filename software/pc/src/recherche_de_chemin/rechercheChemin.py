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
import recherche_de_chemin.fonctions_auxiliaires_fusion as aux

class Cercle:
    def __init__(self,centre,rayon):
        self.centre = centre
        self.rayon = rayon
        
    def copy(self):
        return Cercle(vis.Point(self.centre.x, self.centre.y), self.rayon)
        
class Environnement:
    # côté des polygones qui représentent des cercles, en mm (petit : précision, grand : complexité moindre)
    cote_polygone = 100
    
    def __init__(self):
        self.cercles = []
        self.polygones = []
        
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
    
    def _polygone_du_cercle(cercle):
        """
        méthode de conversion cercle -> polygone
        """
        nbSegments = math.ceil(2*math.pi*cercle.rayon/Environnement.cote_polygone)
        listePointsVi = []
        for i in range(nbSegments):
            theta = -2*math.pi*i/nbSegments+0.01
            x = cercle.centre.x + cercle.rayon*math.cos(theta)
            y = cercle.centre.y + cercle.rayon*math.sin(theta)
            listePointsVi.append(vis.Point(x,y))
        return vis.Polygon(listePointsVi)
        
    def _cercle_circonscrit_du_rectangle(rectangle):
        """
        méthode de conversion rectangle -> cercle circonscrit
        """
        centre = vis.Point((rectangle[0].x + rectangle[2].x)/2,(rectangle[0].y + rectangle[2].y)/2)
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
        a = vis.Point(parcourt["minX"],parcourt["maxY"])
        b = vis.Point(parcourt["maxX"],parcourt["maxY"])
        c = vis.Point(parcourt["maxX"],parcourt["minY"])
        d = vis.Point(parcourt["minX"],parcourt["minY"])
        return Environnement._cercle_circonscrit_du_rectangle([a,b,c,d])
        
    def ajoute_cercle(self, cercle):
        self.cercles.append(cercle)
        self.polygones.append(Environnement._polygone_du_cercle(cercle))
    
    def ajoute_rectangle(self, rectangle):
        self.polygones.append(rectangle)
        self.cercles.append(Environnement._cercle_circonscrit_du_rectangle(rectangle))
        
    def ajoute_polygone(self, listePoints):
        polygone = vis.Polygon(list(map(lambda p: vis.Point(p.x,p.y), listePoints)))
        self.polygones.append(polygone)
        self.cercles.append(Environnement._cercle_circonscrit_du_polygone(polygone))
        
    
class RechercheChemin:
    """
    Classe implémentant une recherche de chemin sur la table. 
    Elle utilise la bibliothèque compilée _visilibity.so, et s'occupe d'ajouter correctement les obstacles sur la table. 
    Elle veille en particulier à fusionner les obstacles adjacents. 
    """
    
    # tolerance de précision (différent de 0.0)
    tolerance = 0.001
    
    def __init__(self,table,config,log):
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        # bords de la carte
        self.bords = vis.Polygon([vis.Point(-self.config["table_x"]/2,0), vis.Point(self.config["table_x"]/2,0), vis.Point(self.config["table_x"]/2,self.config["table_y"]), vis.Point(-self.config["table_x"]/2,self.config["table_y"])])
        
        # environnement initial : obstacles fixes sur la carte
        self.environnement_initial = Environnement()
        # Définition des polygones des obstacles fixes. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
        self._ajoute_obstacle_initial_cercle(vis.Point(0,2000),500)
        self._ajoute_obstacle_initial_rectangle(vis.Polygon([vis.Point(-1500, 0),vis.Point(-1500, 100),vis.Point(-1100, 100),vis.Point(-1100, 0)]))
        self._ajoute_obstacle_initial_rectangle(vis.Polygon([vis.Point(1500, 100),vis.Point(1500, 0),vis.Point(1100, 0),vis.Point(1100, 100)]))
        self._ajoute_obstacle_initial_rectangle(vis.Polygon([vis.Point(-1500, 1900),vis.Point(-1500, 2000),vis.Point(-1100, 2000),vis.Point(-1100, 1900)]))
        self._ajoute_obstacle_initial_rectangle(vis.Polygon([vis.Point(1100, 1900),vis.Point(1100, 2000),vis.Point(1500, 2000),vis.Point(1500, 1900)]))
        
        # environnement dynamique : liste des obstacles mobiles qui sont mis à jour régulièrement
        self.environnement_complet = self.environnement_initial.copy()
        
    def _ajoute_obstacle_initial_cercle(self, centre, rayon):
        cercle = Cercle(centre,rayon)
        self.environnement_initial.ajoute_cercle(cercle)
        self._recouper_aux_bords_table(-1,self.environnement_initial)
    
    def _ajoute_obstacle_initial_rectangle(self, rectangle):
        self.environnement_initial.ajoute_rectangle(rectangle)
        self._recouper_aux_bords_table(-1,self.environnement_initial)
        
    def _recouper_aux_bords_table(self,id,environnement):
        #TODO SUPPRIMER : WATCHDOG
        #alias pour la clarté. Les polygones NE SONT PAS dupliqués (pointeurs)
        poly1 = environnement.polygones[id]
        poly2 = self.bords
        #élection d'un point du poly1 qui ne sort pas de la table
        a1 = None
        for k in range(poly1.n()):
            if collisions.collisionPointPoly(poly1[k],poly2):
                a1 = k
                break
        if not type(a1) == int:
            #Le polygone n'a aucun sommet dans la table. On considère qu'on peut l'ignorer.
            del environnement.polygones[id]
            del environnement.cercles[id]
            return None
        #création de l'obstacle recoupé
        troncateObstacle = []
        #on va considérer le segment allant jusqu'au point voisin de a1
        b1 = aux.avancerSurPolygoneBords(poly1,a1,self.bords)
        WATCHDOG = 0
        auMoinsUneCollision = False
        conditionBouclage = True
        troncateObstacle,conditionBouclage = aux.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
        while conditionBouclage and WATCHDOG < 100:
            WATCHDOG += 1
            print(poly1[a1],poly1[b1])#@
            #input("parcourir ce segment !")#@
            #tests de collision du segment [a1,b1] de poly1 avec les segments de poly2
            collision = False
            pointCollision = None
            for a2 in range(poly2.n()):
                b2 = aux.avancerSurPolygoneBords(poly2,a2,self.bords)
                pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                if pCollision:
                    self.log.critical("collision à "+str(pCollision[1]))#@
                    if type(pCollision[1])==vis.Point:
                        pointCollision = pCollision[1]
                        collision = True
                        auMoinsUneCollision = True
                        break
            if collision:
                troncateObstacle,conditionBouclage = aux.ajouterObstacle(pointCollision,troncateObstacle,conditionBouclage)
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
                    print("collision sur du "+str(poly2.n())+" sur "+str(poly1.n())+" à "+str(pointCollision))#@
                    #input("voir les autres collisions sur le meme segment !")#@
                    collision = False
                    for a2 in range(poly2.n()):
                        b2 = aux.avancerSurPolygoneBords(poly2,a2,self.bords)
                        pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                        if pCollision:
                            if type(pCollision[1])==vis.Point:
                                self.log.warning("autre collision à "+str(pCollision[1]))#@
                                pointCollision = pCollision[1]
                                collision = True
                                break
                    if collision:
                        troncateObstacle,conditionBouclage = aux.ajouterObstacle(pointCollision,troncateObstacle,conditionBouclage)
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
                        troncateObstacle,conditionBouclage = aux.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
                        #parcourt du segment suivant sur l'ex poly2
                        b1 = aux.avancerSurPolygoneBords(poly1,a1,self.bords)
                #------------------------
                
            else :
                self.log.debug("ajout de "+str(poly1[a1])+" au polygone")#@
                #parcourt du segment suivant
                a1 = b1
                b1 = aux.avancerSurPolygoneBords(poly1,a1,self.bords)
                troncateObstacle,conditionBouclage = aux.ajouterObstacle(poly1[a1],troncateObstacle,conditionBouclage)
        if WATCHDOG == 100:
            self.log.critical("récursion non terminale pour le polygone tronqué !")
            raise Exception
        
        for i in range(len(troncateObstacle)):
            if troncateObstacle[i].x < -self.config["table_x"]/2+RechercheChemin.tolerance:
                troncateObstacle[i].x = -self.config["table_x"]/2+2*RechercheChemin.tolerance
            elif troncateObstacle[i].x > self.config["table_x"]/2-RechercheChemin.tolerance:
                troncateObstacle[i].x = self.config["table_x"]/2-2*RechercheChemin.tolerance
            if troncateObstacle[i].y < RechercheChemin.tolerance:
                troncateObstacle[i].y = 2*RechercheChemin.tolerance
            elif troncateObstacle[i].y > self.config["table_y"]-RechercheChemin.tolerance:
                troncateObstacle[i].y = self.config["table_y"]-2*RechercheChemin.tolerance
            
        troncPolygon = vis.Polygon(troncateObstacle)
        environnement.polygones[id] = troncPolygon
        environnement.cercles[id] = Environnement._cercle_circonscrit_du_polygone(troncPolygon)
        
    def _fusionner_avec_obstacles_en_contact(self,sEstDejaRetrouveAuCentre=False):
        #teste le dernier polygone ajouté avec tous les autres, en les parcourant par id décroissant
        for i in range(len(self.environnement_complet.polygones)-2,-1,-1):
            self.log.debug("--> "+str(i))#@
            #test rapide de collision entre les cercles circonscrits aux 2 polygones
            if not collisions.collision_2_cercles(self.environnement_complet.cercles[i],self.environnement_complet.cercles[-1]):
                self.log.warning("pas de collision avec le cercle de l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+".")
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
            if sEstDejaRetrouveAuCentre:
                #commence au point diamétralement opposé
                for k in range(int(poly1.n()/2)):
                    a1 = aux.avancerSurPolygone(poly1,a1)
            
            print("Le parcourt commence sur "+str(poly1.n())+" à "+str(poly1[a1])+" .")#@
            #création de l'obstacle de merge
            mergeObstacle = []
            #on va considérer le segment allant jusqu'au point voisin de a1
            b1 = aux.avancerSurPolygone(poly1,a1)
            WATCHDOG = 0
            auMoinsUneCollision = False
            conditionBouclage = True
            while conditionBouclage and WATCHDOG < 100:
                WATCHDOG += 1
                #tests de collision du segment [a1,b1] de poly1 avec les segments de poly2
                collision = False
                pointCollision = None
                for a2 in range(poly2.n()):
                    b2 = aux.avancerSurPolygone(poly2,a2)
                    pCollision = collisions.collisionSegmentSegment(poly1[a1],poly1[b1],poly2[a2],poly2[b2])
                    if pCollision:
                        if type(pCollision[1])==vis.Point:
                            #point d'intersection entre 2 segments
                            pointCollision = pCollision[1]
                            collision = True,True
                            auMoinsUneCollision = True
                            break
                        elif pCollision[1]=="departsIdentiques":
                            #cas particulier d'une collision sur une extremité du segment
                            poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = aux.segments_meme_origine(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                            collision = True,False
                            break
                        elif pCollision[1]=="segmentsConfondus":
                            #cas particulier de deux segments colinéaires en contact
                            mem = a1
                            poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = aux.segments_confondus(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                            if not a1 == mem:
                                #le cas a été traité dans la fonction auxiliaire
                                collision = True,False
                                break
                                
                if collision:
                    if not collision[1]:
                        #cas particuliers : déjà gérés par une fonction auxiliaire
                        continue
                    mergeObstacle,conditionBouclage = aux.ajouterObstacle(pointCollision,mergeObstacle,conditionBouclage)
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
                            b2 = aux.avancerSurPolygone(poly2,a2)
                            pCollision = collisions.collisionSegmentSegment(pointCollision,poly1[a1],poly2[a2],poly2[b2])
                            if pCollision: 
                                if type(pCollision[1])==vis.Point:
                                    if not pCollision[1] == pointCollision:
                                        self.log.warning("autre collision à "+str(pCollision[1]))#@
                                        pointCollision = pCollision[1]
                                        collision = True,True
                                        break
                                elif pCollision[1]=="departsIdentiques":
                                    #cas particulier d'une collision sur une extremité du segment
                                    poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = aux.segments_meme_origine(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                                    collision = True,False
                                    break
                                elif pCollision[1]=="segmentsConfondus":
                                    #cas particulier de deux segments colinéaires en contact
                                    mem = a1
                                    poly1,poly2,a1,b1,mergeObstacle,conditionBouclage = aux.segments_confondus(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage)
                                    if not a1 == mem:
                                        #le cas a été traité dans la fonction auxiliaire
                                        collision = True,False
                                        break
                            
                        if collision:
                            if not collision[1]:
                                #cas particuliers : déjà gérés par une fonction auxiliaire
                                continue
                            mergeObstacle,conditionBouclage = aux.ajouterObstacle(pointCollision,mergeObstacle,conditionBouclage)
                            #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
                            sopalin = poly1
                            poly1 = poly2
                            poly2 = sopalin
                            #toujours dans le sens horaire : à partir du plus petit indice
                            if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
                            else: a1 = max(a2,b2)
                            self.log.debug("NO WATCHDOG : Changement d'obstacle pour "+str(poly1.n())+". On passe à "+str(poly1[a1]))#@
                        else:
                            continueSurSegment = False
                            mergeObstacle,conditionBouclage = aux.ajouterObstacle(poly1[a1],mergeObstacle,conditionBouclage)
                            #parcourt du segment suivant sur l'ex poly2
                            b1 = aux.avancerSurPolygone(poly1,a1)
                else :
                    #parcourt du segment suivant
                    a1 = b1
                    b1 = aux.avancerSurPolygone(poly1,a1)
                    mergeObstacle,conditionBouclage = aux.ajouterObstacle(poly1[a1],mergeObstacle,conditionBouclage)
                    self.log.debug("On passe à "+str(poly1[a1])+", on attend "+str(mergeObstacle[0]))#@
            if WATCHDOG == 100:
                self.log.critical("récursion non terminale pour le polygone de fusion !")
                raise Exception
                
            if auMoinsUneCollision:
                self.log.warning("cet obstacle rentre en collision avec l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+". Ils ont été fusionnés.")
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
                    if not sEstDejaRetrouveAuCentre:
                        #on retente, avec un point initial diamétralement opposé
                        self._fusionner_avec_obstacles_en_contact(sEstDejaRetrouveAuCentre=True)
                    else:
                        #Et merde... Ben on rattrapera ca avec un environnement de secours (cf get_chemin) -_-'
                        pass
                
            else:
                self.log.warning("cet obstacle ne rentre pas en collision avec l'obstacle "+str(i)+"à "+str(self.environnement_complet.cercles[i].centre)+".")
                
    def ajoute_obstacle_cercle(self, centre, rayon):
        """
        Ajout un obstacle circulaire sur la table.
        Il est considéré comme dynamique et peut etre retiré via retirer_obstacles_dynamiques()
        """
        cercle = Cercle(centre,rayon)
        self.environnement_complet.ajoute_cercle(cercle)
        self._recouper_aux_bords_table(-1,self.environnement_complet)
        self._fusionner_avec_obstacles_en_contact()
            
    def retirer_obstacles_dynamiques(self):
        """
        Retire les obstacles dynamiques et retourne à l'environnement initial
        """
        #on retourne à l'environnement initial, en évitant de le modifier
        self.environnement_complet = self.environnement_initial.copy()
        
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
            
        #conversion en type vis.PointVisibility
        departVis = vis.Point(depart.x,depart.y)
        arriveeVis = vis.Point(arrivee.x, arrivee.y)
        
        # Création de l'environnement, le polygone des bords en premier, ceux des obstacles après (fixes et mobiles)
        env = vis.Environment([self.bords]+self.environnement_complet.polygones)
        
        # Vérification de la validité de l'environnement : polygones non croisés et définis dans le sens des aiguilles d'une montre.
        if not env.is_valid(RechercheChemin.tolerance):
            self.log.critical("Des obstacles invalides ont été trouvés. Ils sont remplacés par leurs cercles contenant.")
            for k in range(len(self.environnement_complet.polygones)):
                #détection du/des polygones défectueux
                if self.environnement_complet.polygones[k].area() >= 0 or not self.environnement_complet.polygones[k].is_simple(RechercheChemin.tolerance):
                    self.log.warning("L'obstacle "+str(k)+" a été remplacé.")
                    #environnement de secours : on remplace le polygone par son cercle contenant
                    self.environnement_complet.polygones[k] = Environnement._polygone_du_cercle(self.environnement_complet.cercles[k])
                    self._recouper_aux_bords_table(k,self.environnement_complet)
            env = vis.Environment([self.bords]+self.environnement_complet.polygones)
        #environnement de secours en cas d'obstacle invalide
        env.is_valid(RechercheChemin.tolerance)
            
        #recherche de chemin
        cheminVis = env.shortest_path(departVis, arriveeVis, RechercheChemin.tolerance)
        
        #conversion en type vis.Point
        chemin = []
        for i in range(1,cheminVis.size()):
            chemin.append(vis.Point(cheminVis[i].x,cheminVis[i].y))
        return chemin