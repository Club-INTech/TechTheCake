import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

from recherche_de_chemin.visilibity import Point
import math

#def collisionPolygonePoint(polygone,point):
    #"""
    #Test de collision point/polygone
    #Par exemple pour l'accessibilité du point d'arrivée sur la table.
    #"""
    #def test_segment(a,b):
        #if ((b.x-a.x)*(point.y-a.y) - (b.y-a.y)*(point.x-a.x) > 0):
            #return False
        #return True
    #for i in range(polygone.n()-1):
        #if not test_segment(polygone[i],polygone[i+1]): return False
    #if not test_segment(polygone[polygone.n()-1],polygone[0]): return False
    #return True
    
def collision_2_cercles(cercle1,cercle2):
    """
    Test de collision cercle/cercle
    Pour dégrossir efficacement les calculs de collision entre obstacles.
    """
    dx = cercle1.centre.x - cercle2.centre.x
    dy = cercle1.centre.y - cercle2.centre.y
    d = math.sqrt(dx**2 + dy**2)
    return d < cercle1.rayon + cercle2.rayon
    
def collisionSegmentSegment(a,b,c,d):
    if a == c:
        return True,"departsIdentiques"
    if a == d or b == c or b == d:
        return False
    else:
        denom  = (d.y-c.y) * (b.x-a.x) - (d.x-c.x) * (b.y-a.y)
        numera = (d.x-c.x) * (a.y-c.y) - (d.y-c.y) * (a.x-c.x)
        numerb = (b.x-a.x) * (a.y-c.y) - (b.y-a.y) * (a.x-c.x)
        eps=0.001

        if (abs(numera) < eps and abs(numerb) < eps and abs(denom) < eps):
            #droites coïncidentes
            #test d'intersection des deux segments colinéraires
            if (((c.x+d.x)/2-(a.x+b.x)/2) > (abs(c.x-d.x)/2+abs(a.x-b.x)/2)) or (((c.y+d.y)/2-(a.y+b.y)/2) > (abs(c.y-d.y)/2+abs(a.y-b.y)/2)) :
                return False
            else:
                return True,"segmentsConfondus"
        elif (abs(denom) < eps):
            #droites parallèles
            return False
        else :
            #point d'intersection
            mua = numera / denom
            mub = numerb / denom
            #inclu dans les deux segments ?
            if (mua <= 0 or mua >= 1 or mub <= 0 or mub >= 1):
                return False
            else:
                pointCollision = Point(a.x+mua*(b.x-a.x),a.y+mua*(b.y-a.y))
                if a == pointCollision or b == pointCollision or c == pointCollision or d == pointCollision:
                    #conventions pour les extrémités
                    return False
                else:
                    return True,pointCollision
                
def collisionPointPoly(point,poly):
    nbCollisions = 0
    for i in range(poly.n()-1):
        if collisionSegmentSegment(Point(10000,10000),point,poly[i],poly[i+1]):
            nbCollisions += 1
    if collisionSegmentSegment(Point(10000,10000),point,poly[poly.n()-1],poly[0]):
        nbCollisions += 1
    #nbCollisions impair : le point est dans le polygone
    return (nbCollisions % 2)