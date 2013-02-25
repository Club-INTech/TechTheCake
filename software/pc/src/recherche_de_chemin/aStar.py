#sudo easy_install-3.2 networkx-1.7-py3.2.egg
import networkx as nx
import math

import outils_maths.point as point #point.Point : format de sortie de la recherche de chemin
from recherche_de_chemin.visilibity import Point #pas de namespace : permet de changer facilement le type Point

#debug #@
#import builtins#@

#def drawLigne(x1,y1,x2,y2):#@
    #builtins.simulateur.drawVector(x1,y1,x2,y2,"green",True)#@
    
class AStar:
    
    pas_x = 300
    pas_y = 200
    
    def _creer_graphe_initial(haut_gauche, bas_droite):
        AStar.minX = haut_gauche[0]
        AStar.maxX = bas_droite[0]
        AStar.minY = bas_droite[1]
        AStar.maxY = haut_gauche[1]
        
        G = nx.Graph()
        
        #première ligne
        y0 = int(AStar.minY+AStar.pas_y/2)
        for x in range(int(AStar.minX+AStar.pas_x/2), int(AStar.maxX-AStar.pas_x),AStar.pas_x):
            G.add_edge((x,y0),(x+AStar.pas_x,y0),weight=AStar.pas_x)
            
        #première colonne
        x0 = int(AStar.minX+AStar.pas_x/2)
        for y in range(int(AStar.minY+AStar.pas_y/2), int(AStar.maxY-AStar.pas_y), AStar.pas_y):
            G.add_edge((x0,y),(x0,y+AStar.pas_y),weight=AStar.pas_y)
                
        #autres arêtes, avec diagonales
        poids_diagonale = int(math.sqrt(AStar.pas_x**2 + AStar.pas_y**2))
        for y in range(int(AStar.minY+3*AStar.pas_y/2), int(AStar.maxY), AStar.pas_y):
            for x in range(int(AStar.minX+3*AStar.pas_x/2), int(AStar.maxX),AStar.pas_x):
                #horizontale
                G.add_edge((x-AStar.pas_x,y),(x,y),weight=AStar.pas_x)
                #verticales
                G.add_edge((x,y-AStar.pas_y),(x,y),weight=AStar.pas_y)
                #diagonale /
                G.add_edge((x-AStar.pas_x,y-AStar.pas_y),(x,y),weight=poids_diagonale)
                #diagonale \
                G.add_edge((x-AStar.pas_x,y),(x,y-AStar.pas_y),weight=poids_diagonale)
        return G
                
    def _noeud_plus_proche(point, G):
        """
        Renvoi le noeud du graphe situé au plus proche du point demandé
        """
        #pour retrouver le noeud au dessous à gauche du point
        kx = int((point.x - (AStar.minX+AStar.pas_x/2))/AStar.pas_x)
        ky = int((point.y - (AStar.minY+AStar.pas_y/2))/AStar.pas_y)
        x1 = (AStar.minX+AStar.pas_x/2) + kx*AStar.pas_x
        y1 = (AStar.minY+AStar.pas_y/2) + ky*AStar.pas_y
        
        #on borne à la table
        bord_droit_x = AStar.maxX - AStar.pas_x/2 - (AStar.maxX-AStar.minX)%AStar.pas_x
        if x1 > bord_droit_x:
            x1 = bord_droit_x
            x2 = x1
        else:
            x2 = x1 + AStar.pas_x
        x1 = max(x1,AStar.minX + AStar.pas_x/2)
        bord_droit_y = AStar.maxY - AStar.pas_y/2 - (AStar.maxY-AStar.minY)%AStar.pas_y
        if y1 > bord_droit_y:
            y1 = bord_droit_y
            y2 = y1
        else:
            y2 = y1 + AStar.pas_y
        y1 = max(y1,AStar.minY + AStar.pas_y/2)
        
        def voisins(p):
            return [
                (p[0]-AStar.pas_x, p[1]+AStar.pas_y),
                (p[0], p[1]+AStar.pas_y),
                (p[0]+AStar.pas_x, p[1]+AStar.pas_y),
                (p[0]+AStar.pas_x, p[1]),
                (p[0]+AStar.pas_x, p[1]-AStar.pas_y),
                (p[0], p[1]-AStar.pas_y),
                (p[0]-AStar.pas_x, p[1]-AStar.pas_y),
                (p[0]-AStar.pas_x, p[1])]
                
        def est_dehors(p):
            return (p[0] > bord_droit_x) or (p[0] < AStar.minX + AStar.pas_x/2) or (p[1] > bord_droit_y) or (p[1] < AStar.minY + AStar.pas_y/2)
            
        positions_a_explorer = [(x1,y1), (x1,y2), (x2,y2), (x2,y1)]
        positions_explorees = positions_a_explorer[:]
        noeuds_a_explorer = []
        while not noeuds_a_explorer:
            for position in positions_a_explorer:
                if position in G.nodes():
                    noeuds_a_explorer.append(position)
                else:
                    frontiere = [p for p in voisins(position) if not (p in positions_explorees or est_dehors(p))]
                    positions_a_explorer += frontiere
                    positions_explorees += frontiere
                #positions_a_explorer.remove(position)
                
        #établissement d'un dictionnaire avec les distances aux noeuds de la liste noeuds_a_explorer
        dico = dict(map(lambda noeud: (AStar._distance_euclidienne(noeud, (point.x,point.y)),noeud),noeuds_a_explorer))

        #on renvoi le noeud le plus proche
        distmin = min(dist for dist in dico.keys())
        return(dico[distmin])
                
        
    def _distance_euclidienne(noeud1, noeud2):
        return math.sqrt((noeud2[0] - noeud1[0])**2 + (noeud2[1] - noeud1[1])**2)
        
    def creer_graphe(haut_gauche, bas_droite, cercles):
        G = AStar._creer_graphe_initial(haut_gauche, bas_droite)
        
        for cercle in cercles:
            noeud_centre = AStar._noeud_plus_proche(cercle.centre, G)
            a_explorer = [noeud_centre]
            while len(a_explorer)>0:
                for noeud in a_explorer:
                    if cercle.contient(Point(noeud[0],noeud[1])):
                        a_explorer += [n for n in G.neighbors(noeud) if not n in a_explorer]
                        G.remove_node(noeud)
                    a_explorer.remove(noeud)
                    
        #for ((x1,y1),(x2,y2)) in G.edges():#@
            #drawLigne(x1,y1,x2,y2)#@
        return G
        
    def plus_court_chemin(depart, arrivee, G):
        Ndepart = AStar._noeud_plus_proche(depart, G)
        Narrivee = AStar._noeud_plus_proche(arrivee, G)
        
        Nchemin = nx.astar_path(G, Ndepart, Narrivee, heuristic=AStar._distance_euclidienne, weight='weight')
        
        chemin = list(map(lambda noeud: point.Point(noeud[0],noeud[1]),Nchemin))
        chemin.append(arrivee)
        return chemin