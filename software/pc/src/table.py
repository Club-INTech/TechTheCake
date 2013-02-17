from time import time
from mutex import Mutex
import math

class Obstacle:

    def __init__(self,position,rayon):
        self.position = position # position est de type Point et pas entier
        self.rayon = rayon
        
class RobotAdverseBalise(Obstacle):
    
    def __init__(self,position,rayon,vitesse):
       Obstacle.__init__(self,position,rayon)
       self.vitesse = vitesse # vitesse est de type Vitesse et pas entier
       
class ObstacleCapteur(Obstacle):
    
    def __init__(self,position,rayon):
       Obstacle.__init__(self,position,rayon)
       self.naissance = time()
       
class Table:
    
    def __init__(self,config,log):
    
        self.config = config
        self.log = log
        self.mutex = Mutex()
        
        # Liste des cadeaux
        self.cadeaux = [	
            {"position": (990,0), "ouvert": False},
            {"position": (390,0), "ouvert": False},
            {"position": (-210,0), "ouvert": False},
            {"position": (-810,0), "ouvert": False}
        ]
            
        self.pointsEntreeCadeaux = [0,3]

        # Listes des obstacles repérés par les différents capteurs 
        self.robotsAdversesBalise = []
        self.obstaclesCapteurs = []
        
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
            {"position":3.010, "traitee":False, "enHaut":False},
            {"position":2.945, "traitee":False, "enHaut":True},
            {"position":2.748, "traitee":False, "enHaut":False},
            {"position":2.552, "traitee":False, "enHaut":True},
            {"position":2.487, "traitee":False, "enHaut":False},
            {"position":2.225, "traitee":False, "enHaut":False},
            {"position":2.159, "traitee":False, "enHaut":True},
            {"position":1.963, "traitee":False, "enHaut":False},
            {"position":1.767, "traitee":False, "enHaut":True},
            {"position":1.701, "traitee":False, "enHaut":False},
            {"position":1.440, "traitee":False, "enHaut":False},
            {"position":1.374, "traitee":False, "enHaut":True},
            {"position":1.178, "traitee":False, "enHaut":False},
            {"position":0.982, "traitee":False, "enHaut":True},
            {"position":0.916, "traitee":False, "enHaut":False},
            {"position":0.654, "traitee":False, "enHaut":False},
            {"position":0.589, "traitee":False, "enHaut":True},
            {"position":0.393, "traitee":False, "enHaut":False},
            {"position":0.196, "traitee":False, "enHaut":True},
            {"position":0.131, "traitee":False, "enHaut":False}
        ]

        # Le premier correspond à celui le plus en haut à gauche et le dernier le plus en bas à droite.
        self.verres = [
            {"position":(600,1050), "present":True},
            {"position":(300,1050), "present":True},
            {"position":(450,800), "present":True},
            {"position":(150,800), "present":True},
            {"position":(600,550), "present":True},
            {"position":(300,550), "present":True},
            {"position":(-600,1050), "present":True},
            {"position":(-300,1050), "present":True},
            {"position":(-450,800), "present":True},
            {"position":(-150,800), "present":True},
            {"position":(-600,550), "present":True},
            {"position":(-300,550), "present":True}
        ]
	
        self.pointsEntreeVerres= [0,5,6,11]

    # A utiliser lorsqu'un cadeau est tombé.
    def cadeau_recupere(self,id) :
        self.cadeaux[id]["ouvert"]=True
        if id in self.pointsEntreeCadeaux :
            self._reattribuePointEntreeCadeaux(id)
	
    # Permet de savoir l'état d'un cadeau.	
    def etat_cadeau(self,id) :
        return self.cadeaux[id]["ouvert"]
	
    # A utiliser lorsqu'une bougie est tombée.
    def bougie_recupere(self,id) :
        self.bougies[id]["traitee"]=True
        if id in self.pointsEntreeBougies :
            self._reattribuePointEntreeBougies(id)
	
    # Permet de savoir l'état d'une bougie.
    def etat_bougie(self,id) :
        return self.bougies[id]["traitee"]

    # A utiliser lorsque notre robot récupère un verre
    def recuperer_verre(self,id) :
        with self.mutex :
            self._retirer_verre(id)
            
    # A utiliser lorsqu'un verre est déjà utilisé (privé).
    def _retirer_verre(self,id) :
            self.verres[id]["present"]=False
            if id in self.pointsEntreeVerres :
                self._reattribuePointEntreeVerres(id)
	
    # Permet de savoir l'état d'un verre.
    def etat_verre(self,id) :
        with self.mutex :
            return self.verres[id]["present"]
 
    # Change l'état du verre si le robot adverse passe trop près.
    def _actualise_verres(self,listeRobots) :
            for k in range(12):
                for robot in listeRobots:
                    dx = self.verres[k]["position"][0] - robot.position.x
                    dy = self.verres[k]["position"][1] - robot.position.y
                    if math.sqrt(dx**2 + dy ** 2) < robot.rayon + self.config["tolerance_verre_actif"] :
                        self._retirer_verre(k)
                
    # Actualise la position et la vitesse des robots adverses.
    def actualise_robotsAdversesBalise(self,positions,vitesses,ids) :
        with self.mutex :
            for id in ids :    
                if id < len(self.robotsAdversesBalise) :
                    self.robotsAdversesBalise[id].position = positions[id]
                    self.robotsAdversesBalise[id].vitesse = vitesses[id]
                else:
                    self.robotsAdversesBalise.append(RobotAdverseBalise(positions[id],self.config["rayon_robot_adverse"],vitesses[id]))
            self._actualise_verres(self.robotsAdversesBalise)
        
    def cree_obstaclesCapteur(self, position) :
        with self.mutex :
            self.obstaclesCapteurs.insert(0,ObstacleCapteur(position,self.config["rayon_robot_adverse"]))
            self._actualise_verres(self.obstaclesCapteurs[:1])
            
    def maj_obstaclesCapteur(self,premierAButer) :
        with self.mutex :
            self.obstaclesCapteurs = self.obstaclesCapteurs[:premierAButer]
        
    def get_obstaclesCapteur(self) :
        with self.mutex :
            return self.obstaclesCapteurs
        
    def get_robotsAdversesBalise(self) :
        with self.mutex :
            return self.robotsAdversesBalise

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
            self.simulateur.drawRectangle(position[0], position[1] + 20, 150, 40, True, "red", "cadeau_" + str(i))
            
        # Affichage des bougies
        for i, bougie in enumerate(self.bougies):
            r = 350 if bougie["enHaut"] else 450
            a = bougie["position"]
            x = r * math.cos(a)
            y = 2000 - r * math.sin(a)
            self.simulateur.drawCircle(x, y, 45, True, "jaune", "bougie_" + str(i))
            
        # Affichage des verres
        for i, verre in enumerate(self.verres):
            position = verre["position"]
            self.simulateur.drawCircle(position[0], position[1], 80, False, "black", "verre_" + str(i))
        
    def cadeau_recupere(self, id):
        Table.cadeau_recupere(self, id)
        self.simulateur.clearEntity("cadeau_" + str(id))
        
    def bougie_recupere(self, id):
        Table.bougie_recupere(self, id)
        self.simulateur.clearEntity("bougie_" + str(id))
        
    def _retirer_verre(self,id):
        Table._retirer_verre(self, id)
        self.simulateur.clearEntity("verre_" + str(id))
