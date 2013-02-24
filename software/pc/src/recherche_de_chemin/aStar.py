#sudo easy_install-3.2 networkx-1.7-py3.2.egg
import networkx as nx
import math

from outils_maths.point import Point

class AStar:
    
    pas_x = 400
    pas_y = 1000
    
    def creer_graphe(haut_gauche, bas_droite, polygones):
        AStar.minX = haut_gauche[0]
        AStar.maxX = bas_droite[0]
        AStar.minY = bas_droite[1]
        AStar.maxY = haut_gauche[1]
        
        G = nx.Graph()
        
        #arretes horizontales
        for y in range(int(AStar.maxY-AStar.pas_y/2), int(AStar.minY), -AStar.pas_y):
            for x in range(int(AStar.minX+AStar.pas_x/2), int(AStar.maxX-AStar.pas_x),AStar.pas_x):
                G.add_edge((x,y),(x+AStar.pas_x,y),weight=AStar.pas_x)
                
        #arretes verticales
        for y in range(int(AStar.maxY-AStar.pas_y/2), int(AStar.minY+AStar.pas_y), -AStar.pas_y):
            for x in range(int(AStar.minX+AStar.pas_x/2), int(AStar.maxX),AStar.pas_x):
                G.add_edge((x,y-AStar.pas_y),(x,y),weight=AStar.pas_y)
                
        #TODO : diagonales
        
        #print(G.edges())
        print("#####")
        print(AStar._noeud_plus_proche(Point(10,800)))
        print(G[AStar._noeud_plus_proche(Point(10,800))])
        
        return G
        
    def _noeud_plus_proche(point):
        """
        Renvoi le noeud du graphe situé au proche du point demandé
        """
        
        #pour retrouver le noeud au dessus à gauche du point
        kx = int((point.x - (AStar.minX+AStar.pas_x/2))/AStar.pas_x)
        ky = int((point.y - (AStar.maxY-AStar.pas_y/2))/AStar.pas_y)
        x = (AStar.minX+AStar.pas_x/2) + kx*AStar.pas_x
        y = (AStar.maxY-AStar.pas_y/2) + ky*AStar.pas_y
        
        #on borne à la table
        x = min(x,AStar.maxX - AStar.pas_x/2 - (AStar.maxX-AStar.minX)%AStar.pas_x)
        x = max(x,AStar.minX + AStar.pas_x/2)
        y = min(y,AStar.maxY - AStar.pas_y/2)
        y = max(y,AStar.minY + AStar.pas_y/2 + (AStar.maxY-AStar.minY)%AStar.pas_y)
        
        #TODO : test de distance euclidienne du point avec [(x,y), (x+1,y), (x,y+1), (x+1,y+1)]
        return (x,y)
        
    def plus_court_chemin(depart, arrivee, G):
        Ndepart = AStar._noeud_plus_proche(depart)
        Narrivee = AStar._noeud_plus_proche(arrivee)
        
        Nchemin = nx.astar_path(G, Ndepart, Narrivee, heuristic=None, weight='weight')
        #TODO : conversion en points
        chemin = []
        #chemin = points(Nchemin)
        chemin.append(arrivee)
        
        return [Point(-600,600),Point(200,700)]