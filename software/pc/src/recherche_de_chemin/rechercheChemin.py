import os,sys

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

from outils_maths.point import Point

#interface C++ avec la fusion de polygones et la recherche de chemin
from recherche_de_chemin.recherche_chemin import VisilibityWrapper
        
class RechercheChemin:
    """
    Classe implémentant une recherche de chemin sur la table. 
    Elle utilise une interface C++ qui implémente une fusion des obstacles avec openCV et une recherche de chemin avec Visilibity. 
    Les obstacles initiaux de la table sont déclarés dans retirer_obstacles_dynamiques(). 
    """
    
    def __init__(self,table,config,log):
        #services nécessaires
        self.table = table
        self.config = config
        self.log = log
        
        #instanciation du wrapper vers openCV et visibility
        #VisilibityWrapper(int width, int height, int ratio, double tolerance_cv, double epsilon_vis, int rayon_tolerance)
        self.wrapper = VisilibityWrapper(self.config["table_x"], self.config["table_y"], 5, 10.0, 0.001, self.config["disque_tolerance_consigne"])
        
        #prise en compte du rayon du robot
        self.rayonRobot = self.config["rayon_robot"]
        
    def ajoute_cercle(self, centre, rayon, dilatationAuto = True):
        """
        Ajoute un obstacle circulaire à l'environnement. 
        """
        if dilatationAuto:
            self.wrapper.add_circle(int(centre.x), int(centre.y), int(rayon + self.rayonRobot))
        else:
            self.wrapper.add_circle(int(centre.x), int(centre.y), int(rayon))
    
    def ajoute_rectangle(self, rectangle, dilatationAuto = True):
        """
        Ajoute un obstacle rectangulaire à l'environnement.  
        """
        #TODO : dilatationAuto
        self.wrapper.add_rectangle(int(rectangle[0].x), int(rectangle[0].y), 
                               int(rectangle[1].x), int(rectangle[1].y),
                               int(rectangle[2].x), int(rectangle[2].y),
                               int(rectangle[3].x), int(rectangle[3].y))
                               
    def retirer_obstacles_dynamiques(self):
        """
        Retire les obstacles dynamiques et retourne à l'environnement initial
        """
        
        # vide le cache de l'environnement
        self.wrapper.reset_environment()
        
        # Redéfinition des polygones des obstacles fixes.
        #gâteau
        self.ajoute_cercle(Point(0,2000),500)
        
        #supports en bois dans les coins
        self.ajoute_rectangle([Point(-1500, 0),Point(-1500, 100+self.rayonRobot),Point(-1100+self.rayonRobot, 100+self.rayonRobot),Point(-1100+self.rayonRobot, 0)], dilatationAuto = False)
        self.ajoute_rectangle([Point(1500, 100+self.rayonRobot),Point(1500, 0),Point(1100-self.rayonRobot, 0),Point(1100-self.rayonRobot, 100+self.rayonRobot)], dilatationAuto = False)
        self.ajoute_rectangle([Point(-1500, 1900-self.rayonRobot),Point(-1500, 2000),Point(-1100+self.rayonRobot, 2000),Point(-1100+self.rayonRobot, 1900-self.rayonRobot)], dilatationAuto = False)
        self.ajoute_rectangle([Point(1100-self.rayonRobot, 1900-self.rayonRobot),Point(1100-self.rayonRobot, 2000),Point(1500, 2000),Point(1500, 1900-self.rayonRobot)], dilatationAuto = False)
        
    def get_obstacles(self):
        """
        (pour affichage de debug) Renvoie la liste des polygones représentant les obstacles
        """
        obstacles = []
        for i in range(self.wrapper.nb_obstacles()):
            obstacle = self.wrapper.get_obstacle(i)
            obstacles.append([Point(obstacle.get_Point(j).x(),obstacle.get_Point(j).y()) for j in range(obstacle.n())])
        return obstacles
        
    def charge_obstacles(self, avec_verres_entrees=True):
        #ajout des obstacles vus par les capteurs et la balise
        for obstacle in self.table.obstacles():
            self.ajoute_cercle(obstacle.position, obstacle.rayon)
        
        ##ajout des obstacles vus par les capteurs (seulement)
        #for obstacle in self.table.obstacles_capteurs:
            #self.ajoute_cercle(obstacle.position, obstacle.rayon)
            
        #ajout des verres encore présents sur la table
        for verre in self.table.verres_restants():
            if avec_verres_entrees or not verre in self.table.verres_entrees():
                self.ajoute_cercle(verre["position"], self.config["rayon_verre"])
        
    def prepare_environnement_pour_visilibity(self):
        if self.wrapper.build_environment() != self.wrapper.RETURN_OK:
            raise ExceptionEnvironnementMauvais 
        
    def cherche_chemin_avec_visilibity(self, depart, arrivee):
        cheminVis = self.wrapper.path(int(depart.x), int(depart.y), int(arrivee.x), int(arrivee.y))
        if cheminVis.size():
            return [Point(cheminVis.get_Point(i).x(),cheminVis.get_Point(i).y()) for i in range(1,cheminVis.size())]
        else:
            raise ExceptionAucunChemin
          
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
        
        self.simulateur.clearEntity("rc_obst")
            
        for obstacle in RechercheChemin.get_obstacles(self):
            for i in range(1,len(obstacle)):
                self.simulateur.drawLine(obstacle[i-1].x,obstacle[i-1].y,obstacle[i].x,obstacle[i].y,"green","rc_obst")
            self.simulateur.drawLine(obstacle[len(obstacle)-1].x,obstacle[len(obstacle)-1].y,obstacle[0].x,obstacle[0].y,"green","rc_obst")
            
    def cherche_chemin_avec_visilibity(self, depart, arrivee):
        chemin = RechercheChemin.cherche_chemin_avec_visilibity(self, depart, arrivee)
        if chemin:
            self.simulateur.clearEntity("rc_chemin")
            for p1,p2 in zip([depart]+chemin[:-1],chemin):
                self.simulateur.drawPoint(p1.x,p1.y,"red","rc_chemin")
                self.simulateur.drawLine(p1.x,p1.y,p2.x,p2.y,"red","rc_chemin")
            self.simulateur.drawPoint(chemin[-1].x,chemin[-1].y,"red","rc_chemin")
        return chemin