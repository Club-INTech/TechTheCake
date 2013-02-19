import recherche_de_chemin.visilibity as vis
import recherche_de_chemin.fonctions_auxiliaires_fusion as fus

import math
from recherche_de_chemin.cercle import Cercle

#DEBUG# import builtins

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
        #DEBUG# builtins.simulateur.drawPoint(bar.x,bar.y,"green",True)#@
        #point recherché :
        polygoneEtendu.append(vis.Point(2*bar.x-polygone[k].x, 2*bar.y-polygone[k].y))
        #DEBUG# builtins.simulateur.drawPoint(2*bar.x-polygone[k].x,2*bar.y-polygone[k].y,"red",True)#@
        
    #on obtient le polygone étendu recherché
    return vis.Polygon(polygoneEtendu)
    
def elargit_polygone(polygone, distance, cote_polygone):
    """
    Renvoit le polygone élargit du polygone donné,
    afin d'adapter la recherche de chemin pour un objet non ponctuel de rayon `distance`.
    
    Le polygone initial n'étant pas forcément convexe, on peut avoir des problèmes dans des cas hyper particuliers, et sortir avec polygone étendu croisé.  
    Mais bon, comme on a PAS de polygones toute facon cette année (autres que des rectangles), avouez que je suis déjà sympa de pisser ca...
    
    Le principe : on cherche la frontière qui reste à `distance` du polygone.
    Pour cela, on considère pour chaque segment un segment parallèle de meme longueur, placé à l'extérieur, 
    Et on ferme aux sommets avec un arc de cercle centré sur le sommet.
    Cet arc de cercle est approximé par un polygone régulier extérieur, afin de limiter le nombre de points.
    On a juste à choisir `ecart_angulaire`, qui définit la précision d'approche de cet arc de cercle.
    """
    
    ecart_angulaire = 0.5*cote_polygone/distance
    
    pointsNormauxA,pointsNormauxB = _etablit_points_normaux(polygone, distance)
    polygoneEtendu = []
    for k in range(len(pointsNormauxA)):
        
        thetaB = math.atan2(pointsNormauxB[k-1].y - polygone[k].y,pointsNormauxB[k-1].x - polygone[k].x)%(2*math.pi)
        thetaA = math.atan2(pointsNormauxA[k].y - polygone[k].y,pointsNormauxA[k].x - polygone[k].x)%(2*math.pi)
        if thetaB > math.pi :thetaB -= 2*math.pi
        if thetaA > math.pi :thetaA -= 2*math.pi
        
        #ajout du point "avant" le sommet
        ecartAB = (thetaB - thetaA)%(2*math.pi)
        if ecartAB > math.pi :ecartAB -= 2*math.pi
        if ecartAB > 0:
            theta1 = thetaB
            theta2 = thetaA
            polygoneEtendu.append(pointsNormauxB[k-1])
            #DEBUG# builtins.simulateur.drawPoint(pointsNormauxB[k-1].x,pointsNormauxB[k-1].y,"green",True)#@
        else:
            theta1 = thetaA
            theta2 = thetaB
            polygoneEtendu.append(pointsNormauxA[k])
            #DEBUG# builtins.simulateur.drawPoint(pointsNormauxA[k].x,pointsNormauxA[k].y,"green",True)#@
        
        #ajout de points supplémentaires sur un arc centré sur le sommet
        thetaPoint = (theta1 - ecart_angulaire)%(2*math.pi)
        ecart = (thetaPoint - theta2)%(2*math.pi)
        if ecart > math.pi :ecart -= 2*math.pi
        while ecart > 0:
            
            #rayon du cercle pour le polygone extérieur (pour etre au moins à `distance`)
            rayonExinscrit = distance*math.sqrt(1+math.sin(ecart_angulaire/4))
            pointX = polygone[k].x + rayonExinscrit*math.cos(thetaPoint)
            pointY = polygone[k].y + rayonExinscrit*math.sin(thetaPoint)
            
            polygoneEtendu.append(vis.Point(pointX, pointY))
            #DEBUG# builtins.simulateur.drawPoint(pointX,pointY,"red",True)#@
            
            thetaPoint = (thetaPoint - ecart_angulaire)%(2*math.pi)
            ecart = (thetaPoint - theta2)%(2*math.pi)
            if ecart > math.pi :ecart -= 2*math.pi
        
        #ajout du point "après" le sommet
        ecartAB = (thetaB - thetaA)%(2*math.pi)
        if ecartAB > math.pi :ecartAB -= 2*math.pi
        if ecartAB > 0:
            polygoneEtendu.append(pointsNormauxA[k])
            #DEBUG# builtins.simulateur.drawPoint(pointsNormauxA[k].x,pointsNormauxA[k].y,"green",True)#@
        else:
            polygoneEtendu.append(pointsNormauxB[k-1])
            #DEBUG# builtins.simulateur.drawPoint(pointsNormauxB[k-1].x,pointsNormauxB[k-1].y,"green",True)#@
        
    #on obtient le polygone étendu recherché
    return vis.Polygon(polygoneEtendu)
    
    
def _etablit_points_normaux(polygone, distance):
    """
    Parcourt le polygone et établit 2 listes de points `normaux`, de sorte que  
    pointsNormauxB[k-1],pointsNormauxA[k] est le segment parallèle à polygone[k-1],polygone[k] 
    placé à `distance` à l'extérieur du polygone.
    """
    pointsNormauxA = []
    pointsNormauxB = []
    a = 0
    for k in range(polygone.n()):
        #le point b est au devant de a sur le polygone
        #DEBUG# builtins.simulateur.drawPoint(polygone[a].x,polygone[a].y,"black",True)#@
        b = fus.avancerSurPolygone(polygone,a)
        
        #détermination du sergment AB et de l'orientation de son vecteur normal
        segmentAB = vis.Point(polygone[b].x-polygone[a].x,polygone[b].y-polygone[a].y)
        orientationSegment = math.atan2(segmentAB.y,segmentAB.x)
        normaleSegment = orientationSegment + math.pi/2
        
        #sauvegarde des points pointNormalA et pointNormalB, formant un segment parallèle à AB et distant de distance
        pointNormalA_X = polygone[a].x + distance*math.cos(normaleSegment)
        pointNormalA_Y = polygone[a].y + distance*math.sin(normaleSegment)
        pointsNormauxA.append(vis.Point(pointNormalA_X,pointNormalA_Y))
        #DEBUG# builtins.simulateur.drawPoint(pointNormalA_X,pointNormalA_Y,"blue",True)#@
        
        pointNormalB_X = polygone[b].x + distance*math.cos(normaleSegment)
        pointNormalB_Y = polygone[b].y + distance*math.sin(normaleSegment)
        pointsNormauxB.append(vis.Point(pointNormalB_X,pointNormalB_Y))
        #DEBUG# builtins.simulateur.drawPoint(pointNormalB_X,pointNormalB_Y,"blue",True)#@
        
        #progression circulaire sur le polygone
        a = fus.avancerSurPolygone(polygone,a)
    
    return pointsNormauxA,pointsNormauxB
    
