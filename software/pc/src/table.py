from time import time
from mutex import Mutex
from outils_maths.point import Point
import math
import copy
import sys

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
        self.derniere_actualisation = time()
        self.vitesse = None
       
    def positionner(self, position, vitesse=None):
        self.position = position
        self.vitesse = vitesse
        self.derniere_actualisation = time()
       
class ObstacleCapteur(Obstacle):
    
    def __init__(self, position, rayon):
       Obstacle.__init__(self, position, rayon)
       self.naissance = time()
       
class Table:
    
    # Masques pour les couleurs des bougies
    COULEUR_BOUGIE_INCONNUE = 1
    COULEUR_BOUGIE_BLANC = 2
    COULEUR_BOUGIE_ROUGE = 4
    COULEUR_BOUGIE_BLEU = 8
    
    # Masques pour les deux zones des verres
    ZONE_VERRE_ROUGE = 1
    ZONE_VERRE_BLEU = 2
    
    def __init__(self, config, log):
    
        self.config = config
        self.log = log
        self.mutex = Mutex()
        
        # Listes des obstacles repérés par les différents capteurs 
        self.robots_adverses = [RobotAdverseBalise(config["rayon_robot_adverse"]), RobotAdverseBalise(3*config["rayon_robot_adverse"]/4)]
        self.obstacles_capteurs = []
        
        # Liste des cadeaux
        self.cadeaux = [	
            {"id": 0, "position": Point(-990,0), "couleur": "bleu", "ouvert": False},
            {"id": 1, "position": Point(-810,0), "couleur": "rouge", "ouvert": False},
            {"id": 2, "position": Point(-390,0), "couleur": "bleu", "ouvert": False},
            {"id": 3, "position": Point(-210,0), "couleur": "rouge", "ouvert": False},
            {"id": 4, "position": Point(210,0), "couleur": "bleu", "ouvert": False},
            {"id": 5, "position": Point(390,0), "couleur": "rouge", "ouvert": False},
            {"id": 6, "position": Point(810,0), "couleur": "bleu", "ouvert": False},
            {"id": 7, "position": Point(990,0), "couleur": "rouge", "ouvert": False}
        ]
        
        # Positions des espaces entre les cadeaux, où on peut rentrer l'actionneur
        self.trous_cadeaux = [
            Point(-600,0),
            Point(0,0),
            Point(600,0)
        ]
            
        # Indique les points d'entrée sur les cadeaux
        # Contient les 2 indices des cadeaux aux extrémités de la table (Xmax, Xmin), même si plus qu'un cadeau
        # Vide si plus aucun cadeau à valider
        self.points_entree_cadeaux = []
        #initialisation
        self._rafraichir_entree_cadeaux()
        
        # La position des bougies est codée en pôlaire depuis le centre du gâteau
        # L'origine de l'angle est l'axe x habituel
        self.bougies = [
            {"id": 0, "position":-3.010, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 1, "position":-2.945, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 2, "position":-2.748, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 3, "position":-2.552, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 4, "position":-2.487, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 5, "position":-2.225, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 6, "position":-2.159, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 7, "position":-1.963, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 8, "position":-1.767, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 9, "position":-1.701, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 10, "position":-1.440, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 11, "position":-1.374, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 12, "position":-1.178, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 13, "position":-0.982, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 14, "position":-0.916, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 15, "position":-0.654, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 16, "position":-0.589, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 17, "position":-0.393, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False},
            {"id": 18, "position":-0.196, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":True},
            {"id": 19, "position":-0.131, "traitee":False, "couleur": Table.COULEUR_BOUGIE_INCONNUE, "enHaut":False}
        ]
        
        # Bougies ignorées car impossible à atteindre
        self.bougies_ignorees = [0, 18]
        
        # Le premier correspond à celui le plus en haut à gauche et le dernier le plus en bas à droite.
        self.verres = [
            {"id": 0, "position": Point(600,1050), "present":True},
            {"id": 1, "position": Point(300,1050), "present":True},
            {"id": 2, "position": Point(450,800), "present":True},
            {"id": 3, "position": Point(150,800), "present":True},
            {"id": 4, "position": Point(300,550), "present":True},
            {"id": 5, "position": Point(600,550), "present":True},
            {"id": 6, "position": Point(-600,1050), "present":True},
            {"id": 7, "position": Point(-300,1050), "present":True},
            {"id": 8, "position": Point(-450,800), "present":True},
            {"id": 9, "position": Point(-150,800), "present":True},
            {"id": 10, "position": Point(-300,550), "present":True},
            {"id": 11, "position": Point(-600,550), "present":True}
        ]
        
        # Positions des centres des cases de départ des robots (ids spécifiés dans la config). Pour le robot rouge (symétrie dans les scripts)
        self.cases_depart = [
            {"centre" : Point(1300,200),  "nb_depots" : 0},
            {"centre" : Point(1300,600),  "nb_depots" : 0},
            {"centre" : Point(1300,1000), "nb_depots" : 0},
            {"centre" : Point(1300,1400), "nb_depots" : 0},
            {"centre" : Point(1300,1800), "nb_depots" : 0}
        ]
        
    def sauvegarder(self):
        """
        Sauvegarde de l'état de la table, utilisé par les scripts chrono qui peuvent modifier l'état de la table
        """
        self.sauvegarde = {
            "verres": copy.deepcopy(self.verres),
            "cases": copy.deepcopy(self.cases_depart)
        }
        
    def restaurer(self):
        """
        Rétablissement de l'état de la table à la dernière sauvegarde
        """
        self.verres = self.sauvegarde["verres"]
        self.cases_depart = self.sauvegarde["cases"]
        
    ###############################################
    ### GESTION DES CADEAUX
    ###############################################
    
    def cadeaux_entrees(self):
        """
        Récupère la liste des cadeaux possibles comme point d'entrée
        """
        return [self.cadeaux[i] for i in self.points_entree_cadeaux]
        
    def cadeaux_restants(self):
        """
        Récupère la liste des cadeaux restants à valider
        """
        return [c for c in self.cadeaux if (not c["ouvert"] and c["couleur"]==self.config["couleur"])]
        
    def cadeau_recupere(self, c):
        """
        Indique qu'un cadeau a été ouvert
        """
        self.cadeaux[c["id"]]["ouvert"] = True
        self.log.debug("cadeau n°{0} ouvert".format(c["id"]))
        self._rafraichir_entree_cadeaux()
        
    def _rafraichir_entree_cadeaux(self):
        """
        Met à jour la liste des points d'entrée pour les cadeaux
        """
        cadeaux_restants = [i for i,c in enumerate(self.cadeaux) if (not c["ouvert"] and c["couleur"]==self.config["couleur"])]
        if len(cadeaux_restants) > 0:
            self.points_entree_cadeaux = [cadeaux_restants[0], cadeaux_restants[-1]]
        else:
            self.points_entree_cadeaux = []
        
    ###############################################
    ### GESTION DES BOUGIES
    ###############################################
    
    def bougies_entrees(self, couleur=COULEUR_BOUGIE_INCONNUE|COULEUR_BOUGIE_BLANC|COULEUR_BOUGIE_ROUGE|COULEUR_BOUGIE_BLEU):
        """
        Récupère la liste des bougies possibles comme point d'entrée
        """
        bougies_restantes = self.bougies_restantes(couleur)
        if len(bougies_restantes) > 0:
            return [bougies_restantes[0], bougies_restantes[-1]]
        else:
            return []
    
    def bougies_restantes(self, couleur=COULEUR_BOUGIE_INCONNUE|COULEUR_BOUGIE_BLANC|COULEUR_BOUGIE_ROUGE|COULEUR_BOUGIE_BLEU):
        """
        Récupère la liste des bougies restantes à valider
        """
        return [b for i,b in enumerate(self.bougies) if i not in self.bougies_ignorees and not b["traitee"] and b["couleur"] & couleur]
        
    def bougie_recupere(self, b):
        """
        Indique que la bougie a été enfoncée
        """
        self.bougies[b["id"]]["traitee"] = True
            
    def definir_couleurs_bougies(self, code):
        """
        Indique la couleur des bougies, avec le format du programme Android
        """

        # On écrase la valeur de l'android si on a entré manuellement une valeur et que l'android donne au moins cinq "?"
        if len(sys.argv) >= 4 and len([i for i in list(code) if i == "?"]) >= 3:
            self.log.warning("Résultats android écrasés par la saisie manuelle")
            code = sys.argv[3]

        conversionIndice = [0, 2, 4, 5, 7, 9, 1, 3, 6, 8]

        if self.config["phases_finales"]:
            nb_blanc_normal = 0
            nb_rouge_normal = 5
        else:
            nb_blanc_normal = 2
            nb_rouge_normal = 4

        # Pour les vérifications (compteur valable pour un côté du gâteau seulement)
        compteur = {
                Table.COULEUR_BOUGIE_INCONNUE : 0,
                Table.COULEUR_BOUGIE_BLANC : 0,
                Table.COULEUR_BOUGIE_ROUGE : 0,
                Table.COULEUR_BOUGIE_BLEU : 0
        }

        conversion = {
                "?": Table.COULEUR_BOUGIE_INCONNUE,
                "w": Table.COULEUR_BOUGIE_BLANC,
                "r": Table.COULEUR_BOUGIE_ROUGE,
                "b": Table.COULEUR_BOUGIE_BLEU
            }
        symetrie = {
                "?": Table.COULEUR_BOUGIE_INCONNUE,
                "w": Table.COULEUR_BOUGIE_BLANC,
                "r": Table.COULEUR_BOUGIE_BLEU,
                "b": Table.COULEUR_BOUGIE_ROUGE
            }
        for i, couleur in enumerate(list(code)):
            # Inversion si on est rouge
            indice = conversionIndice[i]
            if self.config["couleur"] == "rouge":
                indice = 19 - indice
                compteur[symetrie[couleur]] += 1
            else:
                compteur[conversion[couleur]] += 1

            self.bougies[indice]["couleur"] = conversion[couleur]
            self.bougies[19-indice]["couleur"] = symetrie[couleur]

        # On supprime toutes les bougies blanches en en retenant le nombre
        for i in range(10):
            if self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_BLANC:
                self.bougies[i]["couleur"] = Table.COULEUR_BOUGIE_INCONNUE
                self.bougies[19-i]["couleur"] = Table.COULEUR_BOUGIE_INCONNUE
                compteur[Table.COULEUR_BOUGIE_BLANC] -= 1
                compteur[Table.COULEUR_BOUGIE_INCONNUE] += 1

        # On met les bougies blanches là où elles devraient être
        if nb_blanc_normal == 2:
            compteur[self.bougies[7]["couleur"]] -= 1
            compteur[self.bougies[9]["couleur"]] -= 1
            self.bougies[7]["couleur"] = Table.COULEUR_BOUGIE_BLANC
            self.bougies[9]["couleur"] = Table.COULEUR_BOUGIE_BLANC
            self.bougies[10]["couleur"] = Table.COULEUR_BOUGIE_BLANC
            self.bougies[12]["couleur"] = Table.COULEUR_BOUGIE_BLANC
            compteur[Table.COULEUR_BOUGIE_BLANC] += 2
        
        # Ainsi que les bougies extremales de couleurs fixes
            compteur[self.bougies[0]["couleur"]] -= 1
            compteur[self.bougies[1]["couleur"]] -= 1
            self.bougies[0]["couleur"] = Table.COULEUR_BOUGIE_BLEU
            self.bougies[1]["couleur"] = Table.COULEUR_BOUGIE_BLEU
            self.bougies[18]["couleur"] = Table.COULEUR_BOUGIE_ROUGE
            self.bougies[19]["couleur"] = Table.COULEUR_BOUGIE_ROUGE
            compteur[Table.COULEUR_BOUGIE_BLEU] += 2

        # On vérifie qu'on a le bon nombre de couleur. Si on a des bougies de couleur inconnue 
        # et qu'on a par contre toutes les bougies d'une couleur, alors forcément elles sont de l'autre couleur
        if not nb_rouge_normal==compteur[Table.COULEUR_BOUGIE_ROUGE]:
            self.log.warning("Erreur détection bougies rouges! (vues: "+str(compteur[Table.COULEUR_BOUGIE_ROUGE])+")")
        elif compteur[Table.COULEUR_BOUGIE_INCONNUE] != 0:
            self.log.warning("Les bougies inconnues sont supposées bleues")
            compteur[Table.COULEUR_BOUGIE_INCONNUE] = 0
            for i in range(10):
                if self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_INCONNUE:
                    self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_BLEU
                    self.bougies[19-i]["couleur"] == Table.COULEUR_BOUGIE_BLEU
                    compteur[Table.COULEUR_BOUGIE_BLEU] += 1

        if not nb_rouge_normal==compteur[Table.COULEUR_BOUGIE_BLEU]:
            self.log.warning("Erreur détection bougies bleues! (vues: "+str(compteur[Table.COULEUR_BOUGIE_BLEU])+")")
        elif compteur[Table.COULEUR_BOUGIE_INCONNUE] != 0:
            self.log.warning("Les bougies inconnues sont supposées rouges")
            compteur[Table.COULEUR_BOUGIE_INCONNUE] = 0
            for i in range(10):
                if self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_INCONNUE:
                    self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_ROUGE
                    self.bougies[19-i]["couleur"] == Table.COULEUR_BOUGIE_ROUGE
                    compteur[Table.COULEUR_BOUGIE_ROUGE] += 1

        if compteur[Table.COULEUR_BOUGIE_INCONNUE] != 0:
            self.log.warning("Les bougies inconnues sont supposées de la couleur adverse")
            for i in range(10):
                couleur_adverse = Table.COULEUR_BOUGIE_BLEU if self.config["couleur"] == "rouge" else Table.COULEUR_BOUGIE_ROUGE
                if self.bougies[i]["couleur"] == Table.COULEUR_BOUGIE_INCONNUE:
                    self.bougies[i]["couleur"] == couleur_adverse
                    self.bougies[19-i]["couleur"] == couleur_adverse
                    compteur[Table.COULEUR_BOUGIE_INCONNUE] -= 1
                    compteur[couleur_adverse] += 1

    ###############################################
    ### GESTION DES VERRES
    ###############################################
    
    def verres_entrees(self, zone_demandee=ZONE_VERRE_ROUGE|ZONE_VERRE_BLEU):
        """
        Récupère la liste des verres possibles comme point d'entrée sur une des deux zones de la table
        """
        zones = [Table.ZONE_VERRE_ROUGE, Table.ZONE_VERRE_BLEU]
        verres_en_entrees = []
        
        for zone in [z for z in zones if z & zone_demandee]:
            restants_dans_zone = [v["id"] for v in self.verres_restants(zone)]

            if len(restants_dans_zone) == 0:
                pass
            elif len(restants_dans_zone) == 1:
                verres_en_entrees += [self.verres[restants_dans_zone[0]]]
            else:
                verres_en_entrees += [self.verres[min(restants_dans_zone)], self.verres[max(restants_dans_zone)]]
                
        return verres_en_entrees
        
    def verres_restants(self, zone=ZONE_VERRE_ROUGE|ZONE_VERRE_BLEU):
        """
        Récupère les verres restants sur la table
        """
        verres = []
        
        if zone & Table.ZONE_VERRE_ROUGE:
            verres += [v for v in self.verres if v["present"] and v["id"] < 6]
        if zone & Table.ZONE_VERRE_BLEU:
            verres += [v for v in self.verres if v["present"] and v["id"] >= 6]
            
        return verres
        
    def etat_verre(self, verre):
        """
        Indique l'état d'un verre
        """
        with self.mutex:
            return self.verres[verre["id"]]["present"]
            
    def verre_recupere(self, verre):
        """
        Indique qu'un verre a été pris
        """
        self.verres[verre["id"]]["present"] = False
            
    def verre_le_plus_proche(self, position, zone=ZONE_VERRE_ROUGE|ZONE_VERRE_BLEU):
        """
        Récupère le verre le plus proche d'une position
        None est renvoyé si aucun verre présent sur la table dans la zone demandée
        """
        verres = self.verres_restants(zone)
        
        if verres == []:
            return None
            
        choix = verres[0]
        distance_min = position.distance(choix["position"])
        
        # Choix du verre le plus proche et le plus au centre de la table
        # Les verres proches de l'autre zone doivent être récupérés le plus vite
        for verre in verres:
            distance = position.distance(verre["position"])
            if distance - distance_min <= 20 and math.fabs(verre["position"].x) < math.fabs(choix["position"].x):
                choix = verre
                distance_min = distance
                
        return choix

    def _detection_collision_verre(self, position):
        """
        Détecte s'il y a collision entre un robot adverse et un verre sur la table.
        A appeler dès qu'il y a une mise à jour des obstacles.
        """
        pass
        #for i, verre in enumerate(self.verres):
            #if verre["present"]:
                #distance = verre["position"].distance(position)
                #if distance < self.config["rayon_robot_adverse"] + self.config["table_tolerance_verre_actif"]:
                    #self.verre_recupere(verre)
                    
    
    ###############################################
    ### GESTION DES OBSTACLES
    ###############################################
    
    def obstacles(self):
        """
        Récupération de la liste des obstacles sur la table
        """
        with self.mutex:
            obstacles = self.robots_adverses + self.obstacles_capteurs
            return [obstacle for obstacle in obstacles if obstacle.position is not None]
            
    def creer_obstacle(self, position):
        """
        Création d'un obstacle temporaire sur la table
        """
        with self.mutex:
            obstacle = ObstacleCapteur(position, self.config["rayon_robot_adverse"])
            self.obstacles_capteurs.append(obstacle)
            #self._detection_collision_verre(position)
            return obstacle.id
            
    def supprimer_obstacles_perimes(self):
        """
        Mise à jour de la liste des obstacles sur la table
        """
        # Retrait des obstacles des capteurs
        for i, obstacle in enumerate(self.obstacles_capteurs):
            if time() - obstacle.naissance > self.config["duree_peremption_obstacles"]:
                self._supprimer_obstacle(i)
                
        # Retrait des ennemis lasers plus mis à jour
        for i, ennemi in enumerate(self.robots_adverses):
            if time() - ennemi.derniere_actualisation > self.config["duree_peremption_obstacles"]:
                self._supprimer_ennemi(i)
                
    def deplacer_robot_adverse(self, i, position, vitesse=None):
        """
        Mise à jour de la position d'un robot ennemi sur la table
        """
        self.robots_adverses[i].positionner(position,vitesse)
        #if position is not None:
            #self._detection_collision_verre(position)
            
    def _supprimer_obstacle(self, i):
        """
        Suppression d'un obstacle
        """
        with self.mutex:
            self.obstacles_capteurs.pop(i)
            
    def _supprimer_ennemi(self, i):
        """
        Suppression d'un ennemi (laser)
        """
        with self.mutex:
            self.robots_adverses[i].positionner(None)
        
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
        self.simulateur = simulateur
        super().__init__(config, log)
        self._afficher_table()
        self.desactiver_dessin = False
            
    def _afficher_table(self):
        # Affichage des cadeaux
        if self.config["couleur"] == "bleu":
            couleur = "blue"
        else:
            couleur = "red"
        for i, cadeau in enumerate(self.cadeaux):
            if cadeau["couleur"] == self.config["couleur"]:
                self.simulateur.drawRectangle(cadeau["position"].x, cadeau["position"].y + 20, 150, 40, True, couleur, "cadeau_" + str(i))
            
        # Affichage des bougies
        self._dessiner_bougies()
            
        # Affichage des verres
        for i, verre in enumerate(self.verres):
            position = verre["position"]
            self.simulateur.drawCircle(position.x, position.y, 40, False, "black", "verre_" + str(i))
        
    def sauvegarder(self):
        super().sauvegarder()
        self.desactiver_dessin = True
        
    def restaurer(self):
        super().restaurer()
        self.desactiver_dessin = False
        
    def cadeau_recupere(self, c):
        Table.cadeau_recupere(self, c)
        if not self.desactiver_dessin:
            self.simulateur.clearEntity("cadeau_" + str(c["id"]))
        
    def bougie_recupere(self, b):
        Table.bougie_recupere(self, b)
        if not self.desactiver_dessin:
            self.simulateur.clearEntity("bougie_" + str(b["id"]))
        
    def verre_recupere(self, v):
        Table.verre_recupere(self, v)
        if not self.desactiver_dessin:
            self.simulateur.clearEntity("verre_" + str(v["id"]))
        
    def definir_couleurs_bougies(self, code):
        Table.definir_couleurs_bougies(self, code)
        if not self.desactiver_dessin:
            self._dessiner_bougies()
        
    def creer_obstacle(self, position):
        id = Table.creer_obstacle(self, position)
        if not self.desactiver_dessin:
            self.simulateur.drawCircle(position.x, position.y, self.config["rayon_robot_adverse"], False, "black", "obstacle_capteur_"+str(id))
        
    def deplacer_robot_adverse(self, i, position, vitesse=None):
        Table.deplacer_robot_adverse(self, i, position, vitesse)
        
        self.simulateur.clearEntity("ennemi_" + str(i))
        # Mise à jour de la position du robot
        if position is not None:
            with self.mutex:
                ennemi = self.robots_adverses[i]
                couleur = "red" if self.config["couleur"] == "bleu" else "blue"
                self.simulateur.drawCircle(ennemi.position.x, ennemi.position.y, ennemi.rayon, False, couleur, "ennemi_" + str(i))
        
        # Affichage du vecteur vitesse
        if vitesse != None and self.config["lasers_afficher_vecteur_vitesse"]:
            self.simulateur.clearEntity("vitesse_laser")  
            self.simulateur.drawVector(ennemi.position.x, ennemi.position.y, ennemi.position.x + vitesse.vx, ennemi.position.y + vitesse.vy, "black", "vitesse_laser")
        
    def _supprimer_obstacle(self, i):
        try:
            if not self.desactiver_dessin:
                self.simulateur.clearEntity("obstacle_capteur_"+str(self.obstacles_capteurs[i].id))
        except:
            pass
        Table._supprimer_obstacle(self, i)
        
    def _supprimer_ennemi(self, i):
        if not self.desactiver_dessin:
            self.simulateur.clearEntity("ennemi_" + str(i))
        Table._supprimer_ennemi(self, i)
        
    def _dessiner_bougies(self):
        # Suppressions des anciens dessins
        self.simulateur.clearEntity("bougies_couleurs")
            
        for i, bougie in enumerate(self.bougies):
            # Détermination de la position de la bougie
            r = 350 if bougie["enHaut"] else 450
            a = bougie["position"]
            x = r * math.cos(a)
            y = 2000 + r * math.sin(a)
            
            # Dessin du support de bougie
            couleur = {
                Table.COULEUR_BOUGIE_INCONNUE: "black",
                Table.COULEUR_BOUGIE_BLANC: "white",
                Table.COULEUR_BOUGIE_ROUGE: "red",
                Table.COULEUR_BOUGIE_BLEU: "blue"
            }
            self.simulateur.drawCircle(x, y, 40, True, couleur[bougie["couleur"]], "bougies_couleurs")
            
            # Affichage de la balle si la bougie n'est pas enfoncée
            self.simulateur.clearEntity("bougie_" + str(i))
            if not bougie["traitee"]:
                self.simulateur.drawCircle(x, y, 32, True, "jaune", "bougie_" + str(i))
            
