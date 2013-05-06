import os,sys
import math
import copy

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

#bibliothèque de recherche de chemin A* (en python)
import recherche_de_chemin.aStar as aStar

#fonctions auxiliaires pour les calculs géométriques
import recherche_de_chemin.collisions as collisions
import recherche_de_chemin.fonctions_auxiliaires_fusion as fus


from outils_maths.cercle import Cercle
from outils_maths.point import Point

#interface C++ avec la fusion de polygones et la recherche de chemin
from recherche_de_chemin.cpp.recherche_chemin import VisilibityWrapper

class ObstacleCercle:
    
    def __init__(self, cercle, vitesse = None):
        self.circle = cercle
        
    def cercle(self):
        return copy.deepcopy(self.circle)
        
    def charger(self, vis):
        vis.add_circle(self.circle.centre.x, self.circle.centre.y, self.circle.rayon)
        
class ObstacleRectangle:
    
    def __init__(self, sommets):
        self.sommets = sommets
        
    def cercle(self):
        centre = Point((self.sommets[0].x + self.sommets[2].x)/2,(self.sommets[0].y + self.sommets[2].y)/2)
        rayon = math.sqrt((self.sommets[0].x - self.sommets[2].x)**2 + (self.sommets[0].y - self.sommets[2].y)**2)/2.
        return Cercle(centre,rayon)
        
    def charger(self, vis):
        vis.add_rectangle(self.sommets[0].x, self.sommets[0].y, 
                                    self.sommets[1].x, self.sommets[1].y,
                                    self.sommets[2].x, self.sommets[2].y,
                                    self.sommets[3].x, self.sommets[3].y)
    
class Environnement:
    
    def __init__(self, rayonRobot, vis):
        
        #stocke les obstacles de la table.
        self.obstacles = []
        self.vis = vis
        
        #pour dilater les obstacles
        self.rayonRobot = rayonRobot
        
    def ajoute_cercle(self, cercle, dilatationAuto = True):
        """
        Ajoute un obstacle circulaire à l'environnement. 
        """
        if dilatationAuto:
            cercleDilate = Cercle(cercle.centre, cercle.rayon + self.rayonRobot)
            self.obstacles.append(ObstacleCercle(cercleDilate))
            self.obstacles[-1].charger(self.vis)
        else:
            self.obstacles.append(ObstacleCercle(cercle))
            self.obstacles[-1].charger(self.vis)
    
    def ajoute_rectangle(self, rectangle, dilatationAuto = True):
        """
        Ajoute un obstacle rectangulaire à l'environnement.  
        """
        #TODO : dilatationAuto
        self.obstacles.append(ObstacleRectangle(rectangle))
        self.obstacles[-1].charger(self.vis)
        
class RechercheChemin:
    """
    Classe implémentant une recherche de chemin sur la table. 
    Elle utilise une interface C++ qui implémente une fusion des obstacles avec openCV et une recherche de chemin avec Visilibity. 
    Les obstacles initiaux de la table sont déclarés dans son constructeur. 
    """
    
    def __init__(self,table,config,log):
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        #instanciation du wrapper vers openCV et visibility
        #VisilibityWrapper(int width, int height, int ratio, double tolerance_cv, double epsilon_vis, int rayon_tolerance)
        self.vis = VisilibityWrapper(self.config["table_x"], self.config["table_y"], 5, 10.0, 0.0001, self.config["disque_tolerance_consigne"])
        
        #prise en compte du rayon du robot
        self.rayonRobot = self.config["rayon_robot"]
        
    def retirer_obstacles_dynamiques(self):
        """
        Retire les obstacles dynamiques et retourne à l'environnement initial
        """
        # environnement initial : contient les obstacles fixes de la carte
        self.environnement_complet = Environnement(self.rayonRobot, self.vis)
        self.vis.reset_environment()
        
        # Définition des polygones des obstacles fixes. Ils doivent être non croisés et définis dans le sens des aiguilles d'une montre.
        #gâteau
        self.environnement_complet.ajoute_cercle(Cercle(Point(0,2000),500))
        
        #supports en bois dans les coins
        self.environnement_complet.ajoute_rectangle([Point(-1500, 0),Point(-1500, 100+self.rayonRobot),Point(-1100+self.rayonRobot, 100+self.rayonRobot),Point(-1100+self.rayonRobot, 0)], dilatationAuto = False)
        self.environnement_complet.ajoute_rectangle([Point(1500, 100+self.rayonRobot),Point(1500, 0),Point(1100-self.rayonRobot, 0),Point(1100-self.rayonRobot, 100+self.rayonRobot)], dilatationAuto = False)
        self.environnement_complet.ajoute_rectangle([Point(-1500, 1900-self.rayonRobot),Point(-1500, 2000),Point(-1100+self.rayonRobot, 2000),Point(-1100+self.rayonRobot, 1900-self.rayonRobot)], dilatationAuto = False)
        self.environnement_complet.ajoute_rectangle([Point(1100-self.rayonRobot, 1900-self.rayonRobot),Point(1100-self.rayonRobot, 2000),Point(1500, 2000),Point(1500, 1900-self.rayonRobot)], dilatationAuto = False)
        
    def get_cercles_obstacles(self):
        """
        (pour affichage de debug) Renvoie la liste des cercles représentant les obstacles (initiaux et dynamiques)
        """
        return [obstacle.cercle() for obstacle in self.environnement_complet.obstacles]
        
    def get_obstacles(self):
        """
        (pour affichage de debug) Renvoie la liste des polygones représentant les obstacles
        """
        obstacles = []
        for i in range(self.vis.nb_obstacles()):
            obstacle = self.vis.get_obstacle(i)
            obstacles.append([Point(obstacle.get_Point(j).x(),obstacle.get_Point(j).y()) for j in range(obstacle.n())])
        return obstacles
        
    def _lisser_chemin(self, chemin):
        """
        Supprime des noeuds inutiles sur un chemin (formant un angle plat).
        """
        k = 1
        while k < len(chemin)-1:
            angle = fus.get_angle(chemin[k-1],chemin[k],chemin[k+1])
            if angle <= -math.pi+self.config["tolerance_lissage"] or angle >= math.pi-self.config["tolerance_lissage"]:
                chemin.pop(k)
            else: k+=1
        return chemin
        
    ########################## MISE À JOUR DES ÉLÉMENTS DE JEU ##########################
        
    def charge_obstacles(self, avec_verres_entrees=True):
        ##ajout des obstacles vus par les capteurs et la balise
        #for obstacle in self.table.obstacles():
            #self.environnement_complet.ajoute_cercle(Cercle(obstacle.position, obstacle.rayon))
        
        #ajout des obstacles vus par les capteurs (seulement)
        for obstacle in self.table.obstacles_capteurs:
            self.environnement_complet.ajoute_cercle(Cercle(obstacle.position, obstacle.rayon))
            
        #ajout des verres encore présents sur la table
        for verre in self.table.verres_restants():
            if avec_verres_entrees or not verre in self.table.verres_entrees():
                self.environnement_complet.ajoute_cercle(Cercle(verre["position"], self.config["rayon_verre"]))
    
    ####################### PRÉPARATION DE L'ENVIRONNEMENT ET CALCUL DE TRAJET ########################
    
    def prepare_environnement_pour_a_star(self):
        """
        Prépare l'environnement nécessaire aux calculs effectués par l'algorithme de recherche de chemin A*. 
        Cela permet d'effectuer plusieurs recherches de chemin d'affilée sans avoir à recharger les obstacles.
        """
        haut_gauche = int(-self.config["table_x"]/2), int(self.config["table_y"])
        bas_droite = int(self.config["table_x"]/2), int(0)
        self.cercles_astar = [obstacle.cercle() for obstacle in self.environnement_complet.obstacles]
        self.graphe_table = aStar.AStar.creer_graphe(haut_gauche, bas_droite, self.cercles_astar)
        
    def cherche_chemin_avec_a_star(self, depart, arrivee):
        """
        Renvoi un chemin aux arêtes non lissées utilisé pour un calcul rapide de distance (inexploitable pour les scripts). 
        Prend en entrée deux Points depart et arrivee. 
        La sortie est une liste de points à suivre (ne contient pas le point de départ). 
        Une exception est levée si le point d'arrivée n'est pas accessible. 
        """
            
        #test d'accessibilité du point d'arrivée
        if arrivee.x < -self.config["table_x"]/2 or arrivee.y < 0 or arrivee.x > self.config["table_x"]/2 or arrivee.y > self.config["table_y"]:
            self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas dans la table !")
            raise ExceptionArriveeHorsTable
        for obstacle in self.cercles_astar:
            if obstacle.contient(arrivee):
                self.log.critical("Le point d'arrivée "+str(arrivee)+" n'est pas accessible !")
                raise ExceptionArriveeDansObstacle
            
        #recherche de chemin
        if not hasattr(self, 'graphe_table'):
            self.log.critical("Il faut appeler prepare_environnement_pour_a_star() avant cherche_chemin_avec_a_star() !")
            raise ExceptionEnvironnementNonPrepare
        
        try:
            cheminAstar = aStar.AStar.plus_court_chemin(depart, arrivee, self.graphe_table)
            #lissage et suppression du point de départ
            return self._lisser_chemin(cheminAstar)[1:]
        except aStar.ExceptionAucunCheminAstar as e:
            raise ExceptionAucunChemin
        
    def prepare_environnement_pour_visilibity(self):
        if self.vis.build_environment() != self.vis.RETURN_OK:
            raise ExceptionEnvironnementMauvais 
        
    def cherche_chemin_avec_visilibity(self, depart, arrivee):
        cheminVis = self.vis.path(depart.x, depart.y, arrivee.x, arrivee.y)
        return [Point(cheminVis.get_Point(i).x(),cheminVis.get_Point(i).y()) for i in range(1,cheminVis.size())]
          
class ExceptionArriveeHorsTable(Exception):
    """
    Exception levée lorsque le point d'arrivée n'est pas dans la table.
    """
    def __str__(self):
        return "Le point d'arrivée n'est pas dans la table !"

class ExceptionArriveeDansObstacle(Exception):
    """
    Exception levée lorsque le point d'arrivée se situe dans un obstacle.
    """
    def __str__(self):
        return "Le point d'arrivée est dans un obstacle !"
        
class ExceptionDepartDansObstacle(Exception):
    """
    Exception levée lorsque le point de départ se situe dans un obstacle.
    """
    def __str__(self):
        return "Le point de départ est dans un obstacle !"

class ExceptionEnvironnementNonPrepare(Exception):
    """
    Exception levée lorsqu'une méthode de recherche de chemin est appellée avant de préparer l'environnement.
    """
    def __str__(self):
        return "L'environnement de recherche de chemin n'a pas été chargé !"
        
class ExceptionEnvironnementMauvais(Exception):
    """
    Exception levée lorsque le graphe de visibilité pose problème.
    """
    def __str__(self):
        return "L'environnement de recherche de chemin pose problème !"

class ExceptionAucunChemin(Exception):
    """
    Exception levée lorsqu'aucun chemin ne peut relier le départ à l'arrivée.
    """
    def __str__(self):
        return "Aucun chemin possible !"
        
class RechercheCheminSimulation(RechercheChemin):

    def __init__(self, simulateur, table, config, log):
        self.simulateur = simulateur
        super().__init__(table, config, log)
            
    def prepare_environnement_pour_visilibity(self):
        RechercheChemin.prepare_environnement_pour_visilibity(self)
        
        #self.simulateur.clearEntity("rc_obst")
            
        #for obstacle in RechercheChemin.get_obstacles(self):
            #for i in range(1,obstacle.n()):
                #self.simulateur.drawLine(obstacle[i-1].x,obstacle[i-1].y,obstacle[i].x,obstacle[i].y,"green","rc_obst")
            #self.simulateur.drawLine(obstacle[obstacle.n()-1].x,obstacle[obstacle.n()-1].y,obstacle[0].x,obstacle[0].y,"green","rc_obst")
            
    def cherche_chemin_avec_a_star(self, depart, arrivee):
        chemin = RechercheChemin.cherche_chemin_avec_a_star(self, depart, arrivee)
        
        self.simulateur.clearEntity("rc_chemin")
        for p1,p2 in zip([depart]+chemin[:-1],chemin):
            self.simulateur.drawPoint(p1.x,p1.y,"red","rc_chemin")
            self.simulateur.drawLine(p1.x,p1.y,p2.x,p2.y,"red","rc_chemin")
        self.simulateur.drawPoint(chemin[-1].x,chemin[-1].y,"red","rc_chemin")
            
        return chemin
    
    def cherche_chemin_avec_visilibity(self, depart, arrivee):
        chemin = RechercheChemin.cherche_chemin_avec_visilibity(self, depart, arrivee)
        if chemin:
            self.simulateur.clearEntity("rc_chemin")
            for p1,p2 in zip([depart]+chemin[:-1],chemin):
                self.simulateur.drawPoint(p1.x,p1.y,"red","rc_chemin")
                self.simulateur.drawLine(p1.x,p1.y,p2.x,p2.y,"red","rc_chemin")
            self.simulateur.drawPoint(chemin[-1].x,chemin[-1].y,"red","rc_chemin")
            
        return chemin
