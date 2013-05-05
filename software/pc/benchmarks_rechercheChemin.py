#module d'injection de dépendances
from src.container import *
container = Container()
rechercheChemin = container.get_service("rechercheChemin")
table = container.get_service("table")

import math
from time import time,sleep
from outils_maths.point import Point
import recherche_de_chemin.rechercheChemin as libRechercheChemin

##############
#le mode affichage permet d'afficher les obstacles et les chemins sur le simulateur.
#le mode non affichage déclenche une moyenne du benchmark sur plusieurs itérations (pour tester sous ARM)
affichage = True
##############
#nombre d'itération pour moyenner le benchmark en mode non affichage
nbIterations = 50.
#recherche de chemin avec astar ou avec visilibity
aStar = False
##############

if affichage:
    simulateur = container.get_service("simulateur")#@

    def redraw():
        environnement = rechercheChemin.get_obstacles()
        for obstacle in environnement:
            for i in range(1,len(obstacle)):
                simulateur.drawVector(obstacle[i-1].x,obstacle[i-1].y,obstacle[i].x,obstacle[i].y,"green",True)
            simulateur.drawVector(obstacle[len(obstacle)-1].x,obstacle[len(obstacle)-1].y,obstacle[0].x,obstacle[0].y,"green",True)

    def draw_path(depart, arrivee, chemin, color):
        simulateur.drawPoint(depart.x,depart.y, color)
        if chemin:
            simulateur.drawVector(depart.x,depart.y,chemin[0].x,chemin[0].y,color,True)
            print("chemin : ")
            for i in range(len(chemin)):
                print(chemin[i])
                try:simulateur.drawVector(chemin[i].x,chemin[i].y,chemin[i+1].x,chemin[i+1].y,color,True)
                except:pass
        simulateur.drawPoint(arrivee.x,arrivee.y, color)
    
##############################################################################
depart1 = Point(-1000,1300)
arrivee1 = Point(1000,800)

depart2 = Point(-800,1950)
arrivee2 = Point(1050,1350)

depart3 = Point(-1300,400)
arrivee3 = Point(900,300)
##############################################################################

if not affichage:
    print("[moyennes sur "+str(int(nbIterations))+" itérations]")

#nombre d'environnements différents
nbEnvironnements = 3
for i in range(nbEnvironnements):
    if affichage:
        nbIterations = 1.
    
    description = ""
    tempsConception = 0
    tempsChargement = 0
    tempsMoyen3Recherche = 0
    
    for k in range(int(nbIterations)):
        debut_conception = time()
        rechercheChemin.retirer_obstacles_dynamiques()
        if i==0:
            description = "vide"
            rechercheChemin.charge_obstacles()
        elif i==1:
            description = "usuel"
            rechercheChemin.charge_obstacles()
        elif i==2:
            description = "usuel 2"
            try:
                table.verres[1]["present"] = False
                table.verres[9]["present"] = False
                table.verres[8]["present"] = False
                rechercheChemin.charge_obstacles()
            except:
                aStar = True
        debut_chargement = time()
        if aStar: rechercheChemin.prepare_environnement_pour_a_star()
        else: rechercheChemin.prepare_environnement_pour_visilibity()
        debut_recherche_1 = time()
        try:
            if aStar: chemin1 = rechercheChemin.cherche_chemin_avec_a_star(depart1, arrivee1)
            else: chemin1 = rechercheChemin.cherche_chemin_avec_visilibity(depart1, arrivee1)
        except libRechercheChemin.ExceptionAucunChemin as e:
            print(e)
            chemin1 = []
        debut_recherche_2 = time()
        try:
            if aStar: chemin2 = rechercheChemin.cherche_chemin_avec_a_star(depart2, arrivee2)
            else: chemin2 = rechercheChemin.cherche_chemin_avec_visilibity(depart2, arrivee2)
        except Exception as e:
            print(e)
            chemin2 = []
        debut_recherche_3 = time()
        try:
            if aStar: chemin3 = rechercheChemin.cherche_chemin_avec_a_star(depart3, arrivee3)
            else: chemin3 = rechercheChemin.cherche_chemin_avec_visilibity(depart3, arrivee3)
        except Exception as e:
            print(e)
            chemin3 = []
        fin = time()
        tempsConception += round(debut_chargement-debut_conception,3)
        tempsChargement += round(debut_recherche_1-debut_chargement,3)
        tempsMoyen3Recherche += (round(debut_recherche_2-debut_recherche_1,3) + round(debut_recherche_3-debut_recherche_2,3) + round(fin-debut_recherche_3,3))/3
        
        sleep(0.01)
    
    print("environnement "+description+" :\n concu en "+str(round(tempsConception/nbIterations,3))+"\n chargé en "+str(round(tempsChargement/nbIterations,3))+"\n calculé en "+str(round(tempsMoyen3Recherche/nbIterations,3)))
    
    
    if affichage:
        redraw()#@
        draw_path(depart1, arrivee1,chemin1, "red")#@
        draw_path(depart2, arrivee2,chemin2, "black")#@
        draw_path(depart3, arrivee3,chemin3, "blue")#@
    input()
    if affichage:
        simulateur.clearEntities()#@
    rechercheChemin.retirer_obstacles_dynamiques()
    
input("--fin--")
