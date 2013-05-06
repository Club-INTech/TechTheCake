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
            #print("chemin : ")
            for i in range(len(chemin)):
                #print(chemin[i])
                try:simulateur.drawVector(chemin[i].x,chemin[i].y,chemin[i+1].x,chemin[i+1].y,color,True)
                except:pass
        #else:
            #print("chemin : "+str(chemin))
        simulateur.drawPoint(arrivee.x,arrivee.y, color)
    
##############################################################################
depart1 = Point(-1200,1500)
arrivee1 = Point(1000,1250)

depart2 = Point(-800,1950)
arrivee2 = Point(1050,800)

depart3 = Point(-1300,400)
arrivee3 = Point(900,300)
##############################################################################

#nombre d'environnements différents
nbEnvironnements = 4
for i in range(nbEnvironnements):
    if affichage:
        nbIterations = 1.
        nbRecherches = 1
    else:
        nbRecherches = 10
    
    description = ""
    tempsConception = 0
    tempsChargement = 0
    tempsRecherches1 = 0
    tempsRecherches2 = 0
    tempsRecherches3 = 0
    
    nb_reel_iterations = 0
    
    for k in range(int(nbIterations)):
        debut_conception = time()
        rechercheChemin.retirer_obstacles_dynamiques()
        if i==0:
            description = "vide"
        elif i==1:
            description = "avec verres"
            rechercheChemin.charge_obstacles()
        elif i==2:
            description = "verres et robot contre bord"
            rechercheChemin.charge_obstacles()
            rechercheChemin.ajoute_cercle(Point(1200,700), 150)
        elif i==3:
            description = "verres et 2 robots faisant une fat soirée"
            rechercheChemin.ajoute_cercle(Point(1200,700), 150)
            rechercheChemin.ajoute_cercle(Point(-800,1100), 200)
            rechercheChemin.charge_obstacles()
        debut_chargement = time()
        try:
            rechercheChemin.prepare_environnement_pour_visilibity()
            debut_recherche_1 = time()
            try:
                for k in range(nbRecherches):
                    chemin1 = rechercheChemin.cherche_chemin_avec_visilibity(depart1, arrivee1)
            except libRechercheChemin.ExceptionAucunChemin as e:
                #print(e)
                chemin1 = []
            debut_recherche_2 = time()
            try:
                for k in range(nbRecherches):
                    chemin2 = rechercheChemin.cherche_chemin_avec_visilibity(depart2, arrivee2)
            except Exception as e:
                #print(e)
                chemin2 = []
            debut_recherche_3 = time()
            try:
                for k in range(nbRecherches):
                    chemin3 = rechercheChemin.cherche_chemin_avec_visilibity(depart3, arrivee3)
            except Exception as e:
                #print(e)
                chemin3 = []
            fin = time()
            tempsConception += round(debut_chargement-debut_conception,3)
            tempsChargement += round(debut_recherche_1-debut_chargement,3)
            tempsRecherches1 += round(debut_recherche_2-debut_recherche_1,3)
            tempsRecherches2 += round(debut_recherche_3-debut_recherche_2,3)
            tempsRecherches3 += round(fin-debut_recherche_3,3)
            nb_reel_iterations += 1
        except Exception as e:
            print(e)
        
        sleep(0.01)
        
    if not affichage:
        print("[moyennes sur "+str(int(nb_reel_iterations))+" itérations ("+str(int(nbIterations) - nb_reel_iterations)+" fails)]")
    print("environnement "+description+" :\n ajout des obstacles : "+str(round(tempsConception/nb_reel_iterations,3))+"\n établissement du graphe : "+str(round(tempsChargement/nb_reel_iterations,3))+"\n "+str(nbRecherches)+" recherches de chemin : \n\t chemin 1: "+str(round(tempsRecherches1/nb_reel_iterations,3))+"\n\t chemin 2: "+str(round(tempsRecherches2/nb_reel_iterations,3))+"\n\t chemin 3: "+str(round(tempsRecherches3/nb_reel_iterations,3)))
    
    if affichage:
        redraw()#@
        draw_path(depart1, arrivee1,chemin1, "red")#@
        draw_path(depart2, arrivee2,chemin2, "black")#@
        draw_path(depart3, arrivee3,chemin3, "blue")#@
        
    if affichage:
        input()
        simulateur.clearEntities()#@
        
    rechercheChemin.retirer_obstacles_dynamiques()
    
print("--fin--")
