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
    
    def __init__(self, position, rayon):
       Obstacle.__init__(self, position, rayon)
       
class ObstacleCapteur(Obstacle):
    
    def __init__(self, position, rayon):
       Obstacle.__init__(self, position, rayon)
       self.naissance = time()
       
class Table:
    
    def __init__(self, config, log):
    
        self.config = config
        self.log = log
        self.mutex = Mutex()
        
        # Liste des cadeaux en position bleue
        if self.config["couleur"] == "bleu":
            self.cadeaux = [	
                {"position": Point(810,0), "ouvert": False},
                {"position": Point(210,0), "ouvert": False},
                {"position": Point(-390,0), "ouvert": False},
                {"position": Point(-990,0), "ouvert": False}
            ]
            
        # Liste des cadeaux en position rouge
        else:
            self.cadeaux = [	
                {"position": Point(990,0), "ouvert": False},
                {"position": Point(390,0), "ouvert": False},
                {"position": Point(-210,0), "ouvert": False},
                {"position": Point(-810,0), "ouvert": False}
            ]
            
        self.pointsEntreeCadeaux = [0,3]

        # Listes des obstacles repérés par les différents capteurs 
        self.robots_adverses = []
        self.obstacles_capteurs = []
        
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
    
        # Les bougies des côtés sont inaccessibles
        self.pointsEntreeBougies = [2,17]
        
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
	
        self.pointsEntreeVerres= [0,5,6,11]
        
    # Permet de savoir l'état d'un cadeau.	
    def etat_cadeau(self, i):
        return self.cadeaux[i]["ouvert"]
        
    # Permet de savoir l'état d'une bougie.
    def etat_bougie(self, i):
        return self.bougies[i]["traitee"]
        
    # Permet de savoir l'état d'un verre.
    def etat_verre(self, i):
        with self.mutex:
            return self.verres[i]["present"]

    # Indique qu'un cadeau est tombé.
    def cadeau_recupere(self, i):
        self.cadeaux[i]["ouvert"] = True
        if i in self.pointsEntreeCadeaux:
            self._reattribuePointEntreeCadeaux(i)
	
    # Indique qu'une bougie est tombée.
    def bougie_recupere(self, i):
        self.bougies[i]["traitee"] = True
        if i in self.pointsEntreeBougies:
            self._reattribuePointEntreeBougies(i)

    # Indique qu'un verre est récupéré.
    def verre_recupere(self, i):
        with self.mutex:
            self._retirer_verre(i)
            
    # A utiliser lorsqu'un verre est déjà utilisé.
    def _retirer_verre(self, i):
        self.verres[i]["present"] = False
        #~ if i in self.pointsEntreeVerres:
            #~ self._reattribuePointEntreeVerres(i)
 
    # Change l'état du verre si le robot adverse passe trop près.
    def _detection_collision_verre(self, position):
        for i, verre in enumerate(self.verres):
            if verre["present"]:
                distance = verre["position"].distance(position)
                if distance < self.config["rayon_robot_adverse"] + self.config["table_tolerance_verre_actif"]:
                    self._retirer_verre(i)
    
    def definir_couleurs_bougies(self, code):
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
        
    def creer_obstacle(self, position):
        with self.mutex:
            obstacle = ObstacleCapteur(position, self.config["rayon_robot_adverse"])
            self.obstacles_capteurs.append(obstacle)
            self._detection_collision_verre(position)
            return obstacle.id
            
    def supprimer_obstacles_perimes(self):
        for i, obstacle in enumerate(self.obstacles_capteurs):
            if time() - obstacle.naissance > self.config["duree_peremption_obstacles"]:
                self._supprimer_obstacle(i)
            
    def _supprimer_obstacle(self, i):
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
            
    # Récupère la liste des obstacles sur la table
    def obstacles(self):
        with self.mutex:
            return self.robots_adverses + self.obstacles_capteurs

    # Change les points d'entrée pour les verres
    def _reattribuePointEntreeVerres(self, id) :
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

    # Change les points d'entrée pour les bougies
    # Il faut aussi envisager quelques modifs en fonction de si on abandonne définitivement ou pas les bougies aux extrémités.
    def _reattribuePointEntreeBougies(self, id) :
        newId = id
        if id == self.pointsEntreeBougies[0] : # cas où c'est le point d'entrée gauche
            while self.etat_bougie(newId) and newId < 19 :
                newId+=1
            if self.etat_bougie(newId) : # petite manip' au cas où toutes les bougies sont enfoncées.
                newId+=1
            if newId >= 0 and newId < 20 :
                self.pointsEntreeBougies[0] = newId
            else :
                self.pointsEntreeBougies = []
        else : # cas où c'est le point d'entrée droit
            while self.etat_bougie(newId) and newId > 0 :
                newId-=1
            if newId >= 0 and newId < 20 :
                self.pointsEntreeBougies[1] = newId
                
    # Change les points d'entrée pour les cadeaux
    def _reattribuePointEntreeCadeaux(self, id) :
        newId = id
        if id == self.pointsEntreeCadeaux[0] : # cas où c'est le point d'entrée gauche
            while self.etat_cadeau(newId) and newId < 3 :
                newId+=1
            if self.etat_cadeau(newId) : # petite manip' au cas où tous les cadeaux sont renversés.
                newId+=1
            if newId >= 0 and newId < 4 :
                self.pointsEntreeCadeaux[0] = newId
            else :
                self.pointsEntreeCadeaux = []
        else : # cas où c'est le point d'entrée droit
            while self.etat_cadeau(newId) and newId > 0 :
                newId-=1
            if newId >= 0 and newId < 4 :
                self.pointsEntreeCadeaux[1] = newId
                
class TableSimulation(Table):
    
    def __init__(self, simulateur, config, log):
        # Héritage de la classe Table
        self.simulateur = simulateur
        Table.__init__(self, config, log)
        
        # Affichage des cadeaux
        for i, cadeau in enumerate(self.cadeaux):
            position = cadeau["position"]
            couleur = "blue" if self.config["couleur"] == "bleu" else "red"
            self.simulateur.drawRectangle(position.x, position.y + 20, 150, 40, True, couleur, "cadeau_" + str(i))
            
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
        
    def _retirer_verre(self, i):
        Table._retirer_verre(self, i)
        self.simulateur.clearEntity("verre_" + str(i))
        
    def definir_couleurs_bougies(self, code):
        Table.definir_couleurs_bougies(self, code)
        self._dessiner_bougies()
        
    def creer_obstacle(self, position):
        id = Table.creer_obstacle(self, position)
        self.simulateur.drawCircle(position.x, position.y, self.config["rayon_robot_adverse"], False, "black", "obstacle_" + str(id))
        
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
