from time import sleep,time
import math
from outils_maths.point import Point

class Script:
    """
    classe mère des scripts
    se charge des dépendances
    """
    def set_dependencies(self, robot, robotChrono, hookGenerator, rechercheChemin, config, log, table):
        """
        Gère les services nécessaires aux scripts. On n'utilise pas de constructeur.
        """
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.rechercheChemin = rechercheChemin
        self.config = config
        self.log = log
        self.table = table
        
    def va_au_point(self,position):
        """
        Méthode pour atteindre un point de la carte après avoir effectué une recherche de chemin.
        Le chemin n'est pas recalculé s'il a été exploré récemment.
        """
        def calcule_chemin(position):
            self.dernierChemin = self.rechercheChemin.get_chemin(Point(self.robot.x,self.robot.y),position)
            self.dateDernierChemin = time()
        try:
            if self.dernierChemin[-1] != position or time() - self.dateDernierChemin > self.config["duree_peremption_chemin"]:
                #le chemin est périmé et doit être recalculé
                calcule_chemin(position)
        except:
            #le chemin n'a jamais été calculé
            calcule_chemin(position)
        self.robot.suit_chemin(self.dernierChemin)

    def agit(self, *params):
        """
        L'appel script.agit() effectue vraiment les instructions contenues dans execute().
        C'est à dire : envoi de trames sur la série, ou utilisation du simulateur. 
        On peut appeler agit() lorsqu'il n'y a pas de paramètres
        agit(3) pour passer un paramètre (ici entier)
        agit(*(3,"foo","bar")) pour passer n paramètres dans un tuple, qu'on split avec *
        """
        self.robot = self.robotVrai
        self.execute(*params)
        
    def calcule(self):
        """
        L'appel script.calcule() retourne la durée estimée des actions contenues dans execute().
        """
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.robot.maj_x_y_o(self.robotVrai.x, self.robotVrai.y, self.robotVrai.orientation)
        self.execute()
        return self.robot.get_compteur()
    
        
class ScriptBougies(Script):
    """
    exemple de classe de script pour les bougies
    hérite de la classe mère Script
    """
    
    def execute(self,sens):
        """
        Traite le maximum de bougies possibles en partant d'un point d'entrée, et suivant 
        sens : +1 de droite a gauche et -1 de gauche a droite
        """
        #pour les tests
        gateauEnBas = True
        
        rayonAuBras = float(500+self.config["distance_au_gateau"])
        #delta de décalage p/r au centre du robot. On utilise des angles pour inverser plus facilement la direction
        deltaEntree = -20/rayonAuBras
        deltaSortie = 200/rayonAuBras
        deltaPosActionneurBas = +30/rayonAuBras
        deltaPosActionneurHaut = -20/rayonAuBras
        deltaOnBaisse = -20/rayonAuBras
        deltaOnLeve = +30/rayonAuBras
        
        rayon = 500+self.config["distance_au_gateau"]+self.config["longueur_robot"]/2
        if gateauEnBas:
            modifPosYGat = 0
        else:
            modifPosYGat = 2000
        
        idPremiereBougie = self.table.pointsEntreeBougies[int((1+sens)/2)]
        premiereBougie = self.table.bougies[idPremiereBougie]
        angle = premiereBougie["position"] + deltaEntree*sens
        # on se place a la position pour enfoncer la premiere bougie avec une petite marge : on n'effectue pas la symétrie couleur
        
        #on se dirige vers le premier point d'entrée (première bougie)
        mem_effectuer_symetrie = self.robot.effectuer_symetrie
        self.robot.effectuer_symetrie = False
        self.robot.va_au_point(rayon*math.cos(angle), modifPosYGat+rayon*math.sin(angle))
        self.robot.effectuer_symetrie = mem_effectuer_symetrie
        
        #préparer les 2 actionneurs
        self.robot.actionneurs.initialiser_bras_bougie(enHaut = True)
        self.robot.actionneurs.initialiser_bras_bougie(enHaut = False)
        
        hooks = []
        for id in range(len(self.table.bougies)) :
            bougie = self.table.bougies[id]
            if not bougie["traitee"]:
                # on ajoute pour chaque bougie le delta de position de l'actionneur qui correspond
                angleBougie = bougie["position"]+deltaPosActionneurHaut*int(bougie["enHaut"])+deltaPosActionneurBas*(1-int(bougie["enHaut"]))
                #on enregistre un hook de position pour enfoncer une bougie avec un delta de position pour le temps que met l'actionneur
                hooks.append(self.hookGenerator.get_hook("position", Point(rayon*math.cos(angleBougie+deltaOnBaisse*sens), modifPosYGat+rayon*math.sin(angleBougie+deltaOnBaisse*sens)), self.robot.traiter_bougie, id, bougie["enHaut"], unique = True))  
                #on enregistre un hook de position pour relever le bras avec un delta de position pour le temps que met l'actionneur
                hooks.append(self.hookGenerator.get_hook("position", Point(rayon*math.cos(angleBougie+deltaOnLeve*sens), modifPosYGat+rayon*math.sin(angleBougie+deltaOnLeve*sens)), self.robot.initialiser_bras_bougie,bougie["enHaut"], unique = True))    

        idDerniereBougie = self.table.pointsEntreeBougies[int(1-(1+sens)/2)]
        derniereBougie = self.table.bougies[idDerniereBougie]
        angleArc = derniereBougie["position"]+deltaSortie*sens
        # On effectue l'arc de cercle chargé avec la liste des hooks. Marche arrière si besoin, en fonction de la position des actionneurs.
        mem_marche_arriere = self.robot.marche_arriere
        if (sens == 1) != gateauEnBas:
            self.robot.marche_arriere = True
        else:
            self.robot.marche_arriere = False
            
        self.robot.arc_de_cercle(rayon*math.cos(angleArc), modifPosYGat+rayon*math.sin(angleArc),hooks)
        self.robot.tourner(self.robot.orientation + math.pi/2)#on se dégage pour rentrer les actionneurs
        self.robot.marche_arriere = mem_marche_arriere
        #on retire l'actionneur
        self.robot.actionneurs.rentrer_bras_bougie()
        
        #debug
        print("j'ai pété les bougies :")
        for id in range(len(self.table.bougies)) :
            if self.table.bougies[id]["traitee"]:
                print(str(id))
        print("...enfin j'crois...")
        

class ScriptTestHooks(Script):
    
    def execute(self):
            
        def aFaire(texte):
            print("appel du callback : "+texte)
            
        hooks = []
        hooks.append(self.hookGenerator.get_hook("position", Point(910,300), aFaire, "lapin", unique = False))
        hooks.append(self.hookGenerator.get_hook("orientation", math.pi, aFaire, "chèvre"))
        
        self.robot.avancer(300,hooks)
        self.robot.tourner(math.pi/2,hooks)
        self.robot.avancer(500,hooks)
        
        
class ScriptTestCadeaux(Script):
        
    def execute(self):
        
        self.robot.va_au_point(1150,250)

        hooks = []
        hooks.append(self.hookGenerator.get_hook("position", Point(1000,250), self.robot.actionneurs.ouvrir_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(980,250), self.robot.actionneurs.fermer_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(800,250), self.robot.actionneurs.ouvrir_cadeau))
        hooks.append(self.hookGenerator.get_hook("position", Point(780,250), self.robot.actionneurs.fermer_cadeau))
          
        self.robot.avancer(600,hooks)
        
        
class ScriptTestRecalcul(Script):
    
    def execute(self):
        self.va_au_point(Point(0,300))
        self.va_au_point(Point(-100,500))


    #scripts pipeau utilisés dans les test de la stratégie.
class ScriptPipeauStrategie1(Script):
    
    def execute(self):
        self.va_au_point(Point(-500,1000))
        self.robot.ouvrir_cadeau()
        self.va_au_point(Point(-700,1000))
        self.robot.fermer_cadeau()

    def point_entree(self):
        return Point(-500,1000)


class ScriptPipeauStrategie2(Script):
    
    def execute(self):
        self.va_au_point(Point(1000,300))
        self.robot.traiter_bougie()
        
    def point_entree(self):
        return Point(1000,300)


class ScriptPipeauStrategie3(Script):
    
    def execute(self):
        self.va_au_point(Point(500,1500))
        self.robot.traiter_bougie()

    def point_entree(self):
        return Point(500,1500)


