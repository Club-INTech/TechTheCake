from time import time
from mutex import Mutex
from outils_maths.point import Point
import math

class Obstacle:
    
    nombre_instance = 0
    
    def __init__(self, position, rayon):
        Obstacle.nombre_instance += 1
        self.id = Obstacle.nombre_instance
        self.position = position
        self.rayon = rayon
        
class RobotAdverseBalise(Obstacle):
    
    def __init__(self, rayon):
       Obstacle.__init__(self, None, rayon)
       
    def positionner(self, position, vitesse=None):
        self.position = position
        self.vitesse = vitesse
       
class ObstacleCapteur(Obstacle):
    
    def __init__(self, position, rayon):
       Obstacle.__init__(self, position, rayon)
       self.naissance = time()
       
class Table:
    
    def __init__(self, config, log):
    
        self.config = config
        self.log = log
        self.mutex = Mutex()
        
        # Listes des obstacles repérés par les différents capteurs 
        self.robots_adverses = [RobotAdverseBalise(config["rayon_robot_adverse"]), RobotAdverseBalise(3*config["rayon_robot_adverse"]/4)]
        self.obstacles_capteurs = []
        
        # Liste des cadeaux (rouge)
        # La symétrie est gérée dans les scripts
        self.cadeaux = [	
            {"position": Point(990,0), "ouvert": False},
            {"position": Point(390,0), "ouvert": False},
            {"position": Point(-210,0), "ouvert": False},
            {"position": Point(-810,0), "ouvert": False}
        ]
            
        # Indique les points d'entrée sur les cadeaux
        # Contient les 2 indices des cadeaux aux extrémités de la table (Xmax, Xmin), même si plus qu'un cadeau
        # Vide si plus aucun cadeau à valider
        self.points_entree_cadeaux = [0,3]
        
        # La position des bougies est codée en pôlaire depuis le centre du gâteau :
        # (rayon, angle depuis la verticale), elles sont ordonnées par ordre croissant d'angle.
        self.bougies = [
            {"position":-3.010, "traitee":False, "enHaut":False},
            {"position":-2.945, "traitee":False, "enHaut":True},
            {"position":-2.748, "traitee":False, "enHaut":False},
            {"position":-2.552, "traitee":False, "enHaut":True},
            {"position":-2.487, "traitee":False, "enHaut":False},
            {"position":-2.225, "traitee":False, "enHaut":False},
            {"position":-2.159, "traitee":False, "enHaut":True},
            {"position":-1.963, "traitee":False, "enHaut":False},
            {"position":-1.767, "traitee":False, "enHaut":True},
            {"position":-1.701, "traitee":False, "enHaut":False},
            {"position":-1.440, "traitee":False, "enHaut":False},
            {"position":-1.374, "traitee":False, "enHaut":True},
            {"position":-1.178, "traitee":False, "enHaut":False},
            {"position":-0.982, "traitee":False, "enHaut":True},
            {"position":-0.916, "traitee":False, "enHaut":False},
            {"position":-0.654, "traitee":False, "enHaut":False},
            {"position":-0.589, "traitee":False, "enHaut":True},
            {"position":-0.393, "traitee":False, "enHaut":False},
            {"position":-0.196, "traitee":False, "enHaut":True},
            {"position":-0.131, "traitee":False, "enHaut":False}
        ]
    
        # Indique les points d'entrée sur les bougies
        # Contient les 2 indices des bougies aux extrémités du gateau (même si plus qu'une bougie)
        # Vide si plus aucune bougie à valider
        self.points_entree_bougies = [2,17]
        
        # Pour lorsqu'on met le gateau en bas
        self.bougies = [
            {"position":3.010, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":2.945, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":2.748, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":2.552, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":2.487, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":2.225, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":2.159, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":1.963, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":1.767, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":1.701, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":1.440, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":1.374, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":1.178, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":0.982, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":0.916, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":0.654, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":0.589, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":0.393, "traitee":False, "couleur":"?", "enHaut":False},
            {"position":0.196, "traitee":False, "couleur":"?", "enHaut":True},
            {"position":0.131, "traitee":False, "couleur":"?", "enHaut":False}
        ]

        # Le premier correspond à celui le plus en haut à gauche et le dernier le plus en bas à droite.
        self.verres = [
            {"position": Point(600,1050), "present":True},
            {"position": Point(300,1050), "present":True},
            {"position": Point(450,800), "present":True},
            {"position": Point(150,800), "present":True},
            {"position": Point(600,550), "present":True},
            {"position": Point(300,550), "present":True},
            {"position": Point(-600,1050), "present":True},
            {"position": Point(-300,1050), "present":True},
            {"position": Point(-450,800), "present":True},
            {"position": Point(-150,800), "present":True},
            {"position": Point(-600,550), "present":True},
            {"position": Point(-300,550), "present":True}
        ]
	
        self.pointsEntreeVerres = [0,5,6,11]
        
    ###############################################
    ### GESTION DES CADEAUX
    ###############################################
    
    def point_entree_cadeau(self, n):
        """
        Récupère le cadeau correspondant au point d'entrée
        """
        if self.points_entree_cadeaux == []:
            return None
        i = self.points_entree_cadeaux[n]
        
        return self.cadeaux[i]
    
    def cadeaux_restants(self):
        """
        Récupère la liste des cadeaux restants
        """
        return [c for c in self.cadeaux if not c["ouvert"]]
        
    def cadeau_recupere(self, i):
        """
        Indique que le cadeau a été activé
        """
        self.cadeaux[i]["ouvert"] = True
        self._rafraichir_entree_cadeaux()
        
    def _rafraichir_entree_cadeaux(self):
        """
        Met à jour la liste des points d'entrée pour les cadeaux
        """
        cadeaux_restants = [i for i,c in enumerate(self.cadeaux) if not c["ouvert"]]
        if len(cadeaux_restants) > 0:
            self.points_entree_cadeaux = [cadeaux_restants[0], cadeaux_restants[-1]]
        else:
            self.points_entree_cadeaux = []
        
    ###############################################
    ### GESTION DES BOUGIES
    ###############################################
    
    def point_entree_bougie(self, n):
        """
        Récupère la bougie correspondante au point d'entrée
        """
        if self.points_entree_bougies == []:
            return None
        i = self.points_entree_bougies[n]
        
        return self.bougies[i]
    
    def bougies_restantes(self):
        """
        Récupère la liste des bougies restantes
        """
        return [b for b in self.bougies if not b["traitee"]]
        
    def bougie_recupere(self, i):
        """
        Indique que la bougie a été enfoncée
        """
        self.bougies[i]["traitee"] = True
        if i in self.points_entree_bougies:
            self._rafraichir_entree_bougies()
            
    def _rafraichir_entree_bougies(self):
        """
        Met à jour la liste des points d'entrée pour les bougies
        """
        bougies_ignorees = [0, 1, 18, 19]
        bougies_restantes = [i for i,b in enumerate(self.bougies) if not b["traitee"] and i not in bougies_ignorees]
        if len(bougies_restantes) > 0:
            self.points_entree_bougies = [bougies_restantes[0], bougies_restantes[-1]]
        else:
            self.points_entree_bougies = []
            
    def definir_couleurs_bougies(self, code):
        """
        Indique la couleur des bougies, avec le format du programme Android
        """
        for i, couleur in enumerate(list(code)):
            if couleur == "b":
                oppose = "r"
            elif couleur == "r":
                oppose = "b"
            else:
                oppose = couleur
            if self.config["couleur"] == "rouge":
                i = 19-i
            self.bougies[i]["couleur"] = couleur
            self.bougies[19-i]["couleur"] = oppose
            
    ###############################################
    ### GESTION DES VERRES
    ###############################################
    
    def etat_verre(self, i):
        """
        Indique l'état d'un verre
        """
        with self.mutex:
            return self.verres[i]["present"]

    def verre_recupere(self, i):
        """
        Indique qu'un verre a été pris
        """
        self.verres[i]["present"] = False
        self._reattribuePointEntreeVerres(i)
 
    def _detection_collision_verre(self, position):
        """
        Détecte s'il y a collision entre un robot adverse et un verre sur la table.
        A appeler dès qu'il y a une mise à jour des obstacles.
        """
        for i, verre in enumerate(self.verres):
            if verre["present"]:
                distance = verre["position"].distance(position)
                if distance < self.config["rayon_robot_adverse"] + self.config["table_tolerance_verre_actif"]:
                    self.verre_recupere(i)
                    
    # Change les points d'entrée pour les verres
    def _reattribuePointEntreeVerres(self, id):
        """
        C'est la panique ici
        """
        newId = id
        
        if id == self.pointsEntreeVerres[0] : # cas où c'est le point d'entrée gauche chez nous.
            while not self.etat_verre(newId) and newId < 5 :
                newId+=1
            if self.etat_verre(newId) : # petite manip' au cas où tous les verres de la première moitié sont utilisés.
                newId+=1
            if newId >= 0 and newId < 5 :
                self.pointsEntreeVerres[0] = newId
            else :
                if len(self.pointsEntreeVerres) == 4 :
                    self.pointsEntreeVerres = [ -1, -1, self.pointsEntreeVerres[2], self.pointsEntreeVerres[3] ]
                elif len(self.pointsEntreeVerres) == 2 :
                    self.pointsEntreeVerres = []
                    
        elif id == self.pointsEntreeVerres[1] : # cas où c'est le point d'entrée droit chez nous.
            while not self.etat_verre(newId) and newId > 0 :
                newId-=1
            if newId >= 0 and newId < 5 :
                self.pointsEntreeVerres[1] = newId
                
        elif id == self.pointsEntreeVerres[2] : # cas où c'est le point d'entrée gauche chez eux.
            while not self.etat_verre(newId) and newId < 11 :
                newId+=1
            if self.etat_verre(newId) :
                newId+=1
            if newId >= 6 and newId < 11 :
                self.pointsEntreeVerres[2] = newId
            else :
                if len(self.pointsEntreeVerres) == 4 :
                    self.pointsEntreeVerres = [ self.pointsEntreeVerres[0], self.pointsEntreeVerres[1], -1, -1 ]
                elif len(self.pointsEntreeVerres) == 2 :
                    self.pointsEntreeVerres = []
                
        elif id == self.pointsEntreeVerres[3] : # cas où c'est le point d'entrée droit chez eux.
            while not self.etat_verre(newId) and newId > 6 :
                newId-=1
            if newId >= 6 and newId < 11 :
                self.pointsEntreeVerres[3] = newId
    
    ###############################################
    ### GESTION DES OBSTACLES
    ###############################################
    
    def obstacles(self):
        """
        Récupération de la liste des obstacles sur la table
        """
        with self.mutex:
            return self.robots_adverses + self.obstacles_capteurs
            
    def creer_obstacle(self, position):
        """
        Création d'un obstacle temporaire sur la table
        """
        with self.mutex:
            obstacle = ObstacleCapteur(position, self.config["rayon_robot_adverse"])
            self.obstacles_capteurs.append(obstacle)
            self._detection_collision_verre(position)
            return obstacle.id
            
    def supprimer_obstacles_perimes(self):
        """
        Mise à jour de la liste des obstacles temporaires sur la table
        """
        for i, obstacle in enumerate(self.obstacles_capteurs):
            if time() - obstacle.naissance > self.config["duree_peremption_obstacles"]:
                self._supprimer_obstacle(i)
                
    def deplacer_robot_adverse(self, i, position, vitesse=None):
        """
        Mise à jour de la position d'un robot ennemi sur la table
        """
        self.robots_adverses[i].positionner(position)
        self._detection_collision_verre(position)
            
    def _supprimer_obstacle(self, i):
        """
        Suppression d'un obstacle
        """
        with self.mutex:
            self.obstacles_capteurs.pop(i)
        
    def get_obstaclesCapteur(self):
        raise Exception("deprecated, utiliser plutôt obstacles()")
        #~ with self.mutex:
            #~ return self.obstacles_capteurs
        
    def get_robotsAdversesBalise(self):
        raise Exception("deprecated, utiliser plutôt obstacles()")
        #~ with self.mutex:
            #~ return self.robots_adverses
            
                
class TableSimulation(Table):
    
    def __init__(self, simulateur, config, log):
        # Héritage de la classe Table
        self.simulateur = simulateur
        Table.__init__(self, config, log)
        
        # Affichage des cadeaux
        for i, cadeau in enumerate(self.cadeaux):
            position = cadeau["position"]
            if self.config["couleur"] == "bleu":
                couleur = "blue"
                x = -position.x
            else:
                couleur = "red"
                x = position.x
            self.simulateur.drawRectangle(x, position.y + 20, 150, 40, True, couleur, "cadeau_" + str(i))
            
        # Affichage des bougies
        self._dessiner_bougies()
            
        # Affichage des verres
        for i, verre in enumerate(self.verres):
            position = verre["position"]
            self.simulateur.drawCircle(position.x, position.y, 40, False, "black", "verre_" + str(i))
        
    def cadeau_recupere(self, i):
        Table.cadeau_recupere(self, i)
        self.simulateur.clearEntity("cadeau_" + str(i))
        
    def bougie_recupere(self, i):
        Table.bougie_recupere(self, i)
        self.simulateur.clearEntity("bougie_" + str(i))
        
    def verre_recupere(self, i):
        Table.verre_recupere(self, i)
        self.simulateur.clearEntity("verre_" + str(i))
        
    def definir_couleurs_bougies(self, code):
        Table.definir_couleurs_bougies(self, code)
        self._dessiner_bougies()
        
    def creer_obstacle(self, position):
        id = Table.creer_obstacle(self, position)
        self.simulateur.drawCircle(position.x, position.y, self.config["rayon_robot_adverse"], False, "black", "obstacle_" + str(id))
        
    def deplacer_robot_adverse(self, i, position, vitesse=None):
        Table.deplacer_robot_adverse(self, i, position, vitesse)
        
        # Mise à jour de la position du robot
        ennemi = self.robots_adverses[i]
        couleur = "red" if self.config["couleur"] == "bleu" else "blue"
        self.simulateur.clearEntity("ennemi_" + str(i))
        self.simulateur.drawCircle(ennemi.position.x, ennemi.position.y, ennemi.rayon, False, couleur, "ennemi_" + str(i))
        
        # Affichage du vecteur vitesse
        if vitesse != None and self.config["lasers_afficher_vecteur_vitesse"]:
            self.simulateur.clearEntity("vitesse_laser")  
            self.simulateur.drawVector(ennemi.position.x, ennemi.position.y, ennemi.position.x + vitesse.vx, ennemi.position.y + vitesse.vy, "black", "vitesse_laser")
        
    def _supprimer_obstacle(self, i):
        self.simulateur.clearEntity("obstacle_" + str(self.obstacles_capteurs[i].id))
        Table._supprimer_obstacle(self, i)
        
    def _dessiner_bougies(self):
        # Suppressions des anciens dessins
        self.simulateur.clearEntity("bougies_couleurs")
            
        for i, bougie in enumerate(self.bougies):
            # Détermination de la position de la bougie
            r = 350 if bougie["enHaut"] else 450
            a = bougie["position"]
            x = r * math.cos(a)
            y = 2000 - r * math.sin(a)
            
            # Dessin du support de bougie
            if bougie["couleur"] == "r":
                couleur = "red"
            elif bougie["couleur"] == "b":
                couleur = "blue"
            elif bougie["couleur"] == "w":
                couleur = "white"
            else:
                couleur = "black"
            self.simulateur.drawCircle(x, y, 40, True, couleur, "bougies_couleurs")
            
            # Affichage de la balle si la bougie n'est pas enfoncée
            self.simulateur.clearEntity("bougie_" + str(i))
            if not bougie["traitee"]:
                self.simulateur.drawCircle(x, y, 32, True, "jaune", "bougie_" + str(i))
