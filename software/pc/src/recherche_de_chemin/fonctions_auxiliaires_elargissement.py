import recherche_de_chemin.visilibity as vis
import recherche_de_chemin.fonctions_auxiliaires_fusion as fus

import math
from recherche_de_chemin.cercle import Cercle

import builtins
def elargit_cercle(cercle, distance):
    """
    Renvoit le cercle élargit du cercle donné,
    afin d'adapter la recherche de chemin pour un objet non ponctuel de rayon `distance`.
    """
    return Cercle(cercle.centre, cercle.rayon + distance)
    
def elargit_rectangle(polygone, distance):
    """
    Renvoit le rectangle élargit du rectangle donné,
    afin d'adapter la recherche de chemin pour un objet non ponctuel de rayon `distance`.
    """
    pointsNormauxA,pointsNormauxB = _etablit_points_normaux(polygone, distance)
    polygoneEtendu = []
    for k in range(len(pointsNormauxA)):
        #le point recherché est le quatrième du losange qui passe par polygone[i],pointsNormauxA[i] et pointsNormauxB[i-1]
        
        #barycentre de pointsNormauxA[i],pointsNormauxB[i-1] :
        bar = vis.Point((pointsNormauxA[k].x + pointsNormauxB[k-1].x)/2., (pointsNormauxA[k].y + pointsNormauxB[k-1].y)/2.)
        builtins.simulateur.drawPoint(bar.x,bar.y,"green")#@
        #point recherché :
        polygoneEtendu.append(vis.Point(2*bar.x-polygone[k].x, 2*bar.y-polygone[k].y))
        builtins.simulateur.drawPoint(2*bar.x-polygone[k].x,2*bar.y-polygone[k].y,"red")#@
        
    #on obtient le polygone étendu recherché
    return vis.Polygon(polygoneEtendu)
    
def elargit_polygone(polygone, distance):
    """
    Renvoit le polygone élargit du polygone donné,
    afin d'adapter la recherche de chemin pour un objet non ponctuel de rayon `distance`.
    """
    pointsNormauxA,pointsNormauxB = _etablit_points_normaux(polygone, distance)
    #TODO : utiliser ces points et y superposer un cercle à chaque sommet ?
    
    
def _etablit_points_normaux(polygone, distance):
    pointsNormauxA = []
    pointsNormauxB = []
    a = 0
    for k in range(polygone.n()):
        #le point b est au devant de a sur le polygone
        builtins.simulateur.drawPoint(polygone[a].x,polygone[a].y,"black")#@
        b = fus.avancerSurPolygone(polygone,a)
        
        #détermination du sergment AB et de l'orientation de son vecteur normal
        segmentAB = vis.Point(polygone[b].x-polygone[a].x,polygone[b].y-polygone[a].y)
        orientationSegment = math.atan2(segmentAB.y,segmentAB.x)
        normaleSegment = orientationSegment + math.pi/2
        
        #sauvegarde des points pointNormalA et pointNormalB, formant un segment parallèle à AB et distant de distance
        pointNormalA_X = polygone[a].x + distance*math.cos(normaleSegment)
        pointNormalA_Y = polygone[a].y + distance*math.sin(normaleSegment)
        pointsNormauxA.append(vis.Point(pointNormalA_X,pointNormalA_Y))
        builtins.simulateur.drawPoint(pointNormalA_X,pointNormalA_Y,"blue")#@
        
        pointNormalB_X = polygone[b].x + distance*math.cos(normaleSegment)
        pointNormalB_Y = polygone[b].y + distance*math.sin(normaleSegment)
        pointsNormauxB.append(vis.Point(pointNormalB_X,pointNormalB_Y))
        builtins.simulateur.drawPoint(pointNormalB_X,pointNormalB_Y,"blue")#@
        
        #progression circulaire sur le polygone
        a = fus.avancerSurPolygone(polygone,a)
    
    return pointsNormauxA,pointsNormauxB
    
