import recherche_de_chemin.visilibity as vis
import recherche_de_chemin.collisions as collisions

def get_angle(a,o,b):
    oa = Point(a.x-o.x,a.y-o.y)
    ob = Point(b.x-o.x,b.y-o.y)
    theta = math.atan2(ob.y,ob.x) - math.atan2(oa.y,oa.x)
    if theta > math.pi :theta -= 2*math.pi
    elif theta <= -math.pi :theta += 2*math.pi
    return theta
    
def ps(v1,v2):
    return v1.x*v2.x + v1.y*v2.y
    
def avancerSurPolygone(poly,position):
    if position < poly.n()-1: return position + 1
    else: return 0
    
def avancerSurPolygoneBords(poly,position,bords):
    if poly == bords:
        if position > 0: return position - 1
        else: return poly.n()-1
    else:
        if position < poly.n()-1: return position + 1
        else: return 0
        
def ajouterObstacle(point,obstacle,conditionBouclage):
    try:
        if point == obstacle[0]:
            conditionBouclage = False
        else:
            if conditionBouclage:
                obstacle.append(point)
    except:
        obstacle.append(point)
    return obstacle,conditionBouclage

def segments_meme_origine(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage):
    #les deux segments partent du même point : on choisit le segment qui "ouvre" le plus le polygone
    theta = get_angle(poly1[b1],poly1[a1],poly2[b2])
    if theta == 0:
        #on choisit le plus long des deux segments
        r1 = (poly1[b1].x - poly1[a1].x)**2 + (poly1[b1].y - poly1[a1].y)**2
        r2 = (poly2[b2].x - poly2[a2].x)**2 + (poly2[b2].y - poly2[a2].y)**2
        if r1 < r2:
            #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
            sopalin = poly1
            poly1 = poly2
            poly2 = sopalin
            #toujours dans le sens horaire : à partir du plus petit indice
            #if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
            #else: a1 = max(a2,b2)
            a1 = a2
            b1 = b2
        else:
            #parcourt du segment suivant
            a1 = b1
            b1 = avancerSurPolygone(poly1,a1)
            mergeObstacle,conditionBouclage = ajouterMergeObstacle(poly1[a1],mergeObstacle,conditionBouclage)
    elif theta > 0:
        #on parcourt l'autre polygone, en inversant les pointeurs sur poly1 et poly2
        sopalin = poly1
        poly1 = poly2
        poly2 = sopalin
        #toujours dans le sens horaire : à partir du plus petit indice
        #if 0 in [a2,b2] and poly1.n()-1 in [a2,b2]: a1 = 0
        #else: a1 = max(a2,b2)
        a1 = a2
        b1 = b2
    else:
        #parcourt du segment suivant
        a1 = b1
        b1 = avancerSurPolygone(poly1,a1)
        mergeObstacle,conditionBouclage = ajouterMergeObstacle(poly1[a1],mergeObstacle,conditionBouclage)
    return poly1,poly2,a1,b1,mergeObstacle,conditionBouclage
    
def segments_confondus(poly1,poly2,a1,b1,a2,b2,mergeObstacle,conditionBouclage):
    #input("segments ["+str(poly1[a1])+", "+str(poly1[b1])+"] et ["+str(poly2[a2])+", "+str(poly2[b2])+"] confondus !")#@
    #vecteurs
    ab1 = vis.Point(poly1[b1].x - poly1[a1].x, poly1[b1].y - poly1[a1].y)
    ab2 = vis.Point(poly2[b2].x - poly1[a1].x, poly2[b2].y - poly1[a1].y)
    if ps(ab1,ab2) >= ps(ab1,ab1):
        #cas où b1 survient avant b2, dans l'alignement
        c1 = avancerSurPolygone(poly1,b1)
        theta = get_angle(poly2[b2],poly1[b1],poly1[c1])
        if theta >= 0:
            #le segment [b1,c1] 'ouvre' plus le polygone : on conserve ce segment
            mergeObstacle,conditionBouclage = ajouterMergeObstacle(poly1[b1],mergeObstacle,conditionBouclage)
            a1 = b1
            b1 = c1
        else:
            #le segment [b1,c1] rentre dans le polygone : on considère la fin de l'alignement, sur poly2
            sopalin = poly1
            poly1 = poly2
            poly2 = sopalin
            a1 = a2
            b1 = b2
    else:
        #cas où b2 survient avant b1, dans l'alignement
        c2 = avancerSurPolygone(poly2,b2)
        theta = get_angle(poly1[b1],poly2[b2],poly2[c2])
        if theta <= 0:
            #le segment [b2,c2] rentre dans le polygone : on observe les autres collisions de [a1,b1] avec les autres segments de poly2
            pass
        else:
            #le segment [b2,c2] 'ouvre' plus le polygone : on ajoute b2 et passe sur poly2
            mergeObstacle,conditionBouclage = ajouterMergeObstacle(poly2[b2],mergeObstacle,conditionBouclage)
            sopalin = poly1
            poly1 = poly2
            poly2 = sopalin
            a1 = b2
            b1 = c2
    return poly1,poly2,a1,b1,mergeObstacle,conditionBouclage