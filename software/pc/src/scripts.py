import inspect
import sys
import math
import abc

from time import sleep,time
from outils_maths.point import Point
import table
import robot


class Script(metaclass=abc.ABCMeta):
    """
    classe mère des scripts
    se charge des dépendances
    """
    def dependances(self, simulateur, robot, robotChrono, hookGenerator, table, config, log):
        """
        Gère les services nécessaires aux scripts. On n'utilise pas de constructeur.
        """
        self.simulateur = simulateur
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.table = table
        self.config = config
        self.log = log

    def agit(self, version):
        """
        L'appel script.agit() effectue vraiment les instructions contenues dans _execute().
        Les paramètres de agit() sont les mêmes que ceux envoyés à _execute()
        """
        self.robot = self.robotVrai
        try:
            self._execute(version)
        except robot.ExceptionMouvementImpossible:
            raise robot.ExceptionMouvementImpossible
        finally:
            self._termine()
        
    def calcule(self, version):
        """
        L'appel script.calcule() retourne la durée estimée des actions contenues dans executer().
        """
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.robot.maj_x_y_o(self.robotVrai.x, self.robotVrai.y, self.robotVrai.orientation)
        self.robot.maj_capacite_verres(self.robotVrai.nb_verres_avant, self.robotVrai.nb_verres_arriere)
        
        try:
            self.table.sauvegarder()
            self._execute(version)
        except Exception as e:
            raise e
        finally:
            self.table.restaurer()
        
        return self.robot.get_compteur()

    @abc.abstractmethod
    def versions(self):
        pass
        
    @abc.abstractmethod
    def point_entree(self, id_version):
        pass
        
    @abc.abstractmethod
    def score(self):
        pass
        
    @abc.abstractmethod
    def _termine(self):
        pass

    @abc.abstractmethod
    def _execute(self, id_version):
        pass

    @abc.abstractmethod
    def poids(self):
        pass

             
class ScriptManager:
    
    def __init__(self, simulateur, robot, robotChrono, hookGenerator, table, config, log):
        self.log = log
        self.scripts = {}
        
        # Instanciation automatique des classes héritant de Script
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for nom, obj in classes:
            heritage = list(inspect.getmro(obj))
            if not inspect.isabstract(obj) and Script in heritage:
                self.scripts[nom] = obj()
                self.scripts[nom].dependances(simulateur, robot, robotChrono, hookGenerator, table, config, log)


class ScriptBougies(Script):
   
    def _execute(self, version):

        # Il n'y a aucune symétrie sur la couleur dans les déplacements
        self.robot.marche_arriere = False
        self.robot.effectuer_symetrie = False
        
        # Déplacement vers le point d'entrée avec recherche de chemin
        entree = self.info_versions[version]["point_entree_recherche_chemin"]
        self.robot.recherche_de_chemin(entree, False)
        
        # Déplacement vers le point d'entrée
        entree = self.info_versions[version]["point_entree"]
        sortie = self.info_versions[1-version]["point_entree"]
        self.robot.va_au_point(entree)
        
        # Hooks sur chaque bougie à enfoncer
        rayon_bras = float(500 + self.config["distance_au_gateau"])
        delta_angle_baisser_bras = -15 / rayon_bras
        delta_angle_lever_bras = 30 / rayon_bras
        hooks = []
        
        # Récupération des bougies restantes dans notre couleur
        for bougie in self.table.bougies_restantes(self.couleur_a_traiter):
            
            # Baisser le bras
            point_baisser_bras = self._correspondance_point_angle(bougie["position"] + delta_angle_baisser_bras, self.config["distance_au_gateau"])
            hook_baisser_bras = self.hookGenerator.hook_position(point_baisser_bras)
            hook_baisser_bras += self.hookGenerator.callback(self.robot.traiter_bougie, (bougie["enHaut"],))
            hook_baisser_bras += self.hookGenerator.callback(self.table.bougie_recupere, (bougie,))
            hooks.append(hook_baisser_bras)
            
            # Lever le bras
            #~ point_lever_bras = self._correspondance_point_angle(bougie["position"] + delta_angle_lever_bras)
            #~ hook_lever_bras = self.hookGenerator.hook_position(point_lever_bras)
            #~ hook_lever_bras += self.hookGenerator.callback(self.robot.initialiser_bras_bougie(bougie["enHaut"]))
            #~ hooks.append(hook_lever_bras)
        
        # Lancement de l'arc de cercle
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        self.robot.arc_de_cercle(sortie, hooks)
        
        """
        gateauEnBas = False
        
        rayonAuBras = float(500+self.config["distance_au_gateau"])
        #delta de décalage p/r au centre du robot. On utilise des angles pour inverser plus facilement la direction
        deltaEntree = -20/rayonAuBras
        deltaSortie = 20/rayonAuBras
        deltaPosActionneurBas = +30/rayonAuBras
        deltaPosActionneurHaut = -20/rayonAuBras
        deltaOnBaisse = -15/rayonAuBras
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
        self.robot.initialiser_bras_bougie(enHaut = True)
        self.robot.initialiser_bras_bougie(enHaut = False)
        hooks = []
        
        print("je vais enfoncer :")
        for id in range(len(self.table.bougies)) :
            bougie = self.table.bougies[id]
            if not bougie["traitee"]:
                print(id)
                # on ajoute pour chaque bougie le delta de position de l'actionneur qui correspond
                angleBougie = bougie["position"]+deltaPosActionneurHaut*int(bougie["enHaut"])+deltaPosActionneurBas*(1-int(bougie["enHaut"]))
                #on enregistre un hook de position pour enfoncer une bougie avec un delta de position pour le temps que met l'actionneur
                hooks.append(self.hookGenerator.get_hook("position", Point(rayon*math.cos(angleBougie+deltaOnBaisse*sens), modifPosYGat+rayon*math.sin(angleBougie+deltaOnBaisse*sens)), self.robot.traiter_bougie, id, bougie["enHaut"], unique = True))  
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
        #on se dégage pour rentrer les actionneurs
        self.robot.tourner(self.robot.orientation + math.pi/2,forcer = True)
        self.robot.marche_arriere = mem_marche_arriere
        #on retire l'actionneur
        self.robot.rentrer_bras_bougie()

        #debug
        print("j'ai pété les bougies :")
        for id in range(len(self.table.bougies)) :
            if self.table.bougies[id]["traitee"]:
                print(str(id))
        print("...enfin j'crois...")
        """
        
    def _correspondance_point_angle(self, angle, distance_gateau):
        """
        Retourne le point sur la table correspondant à un angle de bougie
        """
        rayon = 500 + distance_gateau + self.config["longueur_robot"] / 2
        return Point(0, 2000) + Point(rayon * math.cos(angle), rayon * math.sin(angle))

    def _termine(self):
        pass
        
    def versions(self):
        """
        Récupération des versions du script
        - [] si aucune bougie à valider
        - 2 versions sinon, où le gateau est parcouru dans un sens différent en validant toutes les bougies restantes
        """
        # Récupération des bougies restantes
        self.couleur_a_traiter = self.table.COULEUR_BOUGIE_ROUGE if self.config["couleur"] == "rouge" else self.table.COULEUR_BOUGIE_BLEU
        bougies = self.table.bougies_entrees(self.couleur_a_traiter)

        # Cas où toutes les bougies sont déjà validées
        if bougies == []:
            return []
            
        # Cas où il reste au moins une bougie
        delta_angle = 20 / float(500 + self.config["distance_au_gateau"])
        self.info_versions = [
            {
                "angle_entree": bougies[0]["position"] - delta_angle,
                "point_entree": self._correspondance_point_angle(bougies[0]["position"] - delta_angle, self.config["distance_au_gateau"]),
                "point_entree_recherche_chemin": self._correspondance_point_angle(bougies[0]["position"] - delta_angle, self.config["distance_au_gateau"] + 100),
                "marche_arriere": False,
                "sens": 1
            },               
            {
                "angle_entree": bougies[1]["position"] + delta_angle,
                "point_entree": self._correspondance_point_angle(bougies[1]["position"] + delta_angle, self.config["distance_au_gateau"]),
                "point_entree_recherche_chemin": self._correspondance_point_angle(bougies[1]["position"] + delta_angle, self.config["distance_au_gateau"] + 100),
                "marche_arriere": True,
                "sens": -1
            }
        ]
        
        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
        
    def score(self):
        return 4 * len([element for element in self.table.bougies_restantes(self.couleur_a_traiter)])
    
    def poids(self):
        return 1

class ScriptCadeaux(Script):
        
    def _execute(self, version):
        
        # Effectue une symétrie sur tous les déplacements
        self.robot.effectuer_symetrie = True
        # Déplacement vers le point d'entrée
        self.robot.marche_arriere = False
        self.robot.recherche_de_chemin(self.info_versions[version]["point_entree_recherche_chemin"], recharger_table=False)
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(self.info_versions[version]["point_entree"], 0)
        self.robot.va_au_point(self.info_versions[version]["point_entree"])

        # Orientation du robot
        sens = self.info_versions[version]["sens"]
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        
        # Création des hooks pour tous les cadeaux à activer
        hooks = []
        for cadeau in self.table.cadeaux_restants():
            
            # Ouverture du bras
            hook_ouverture = self.hookGenerator.hook_position(cadeau["position"] + Point(sens * self.decalage_x_ouvre, self.decalage_y_bord ), effectuer_symetrie=(self.config["couleur"] == "bleu"))
            hook_ouverture += self.hookGenerator.callback(self.robot.ouvrir_cadeau)
            hook_ouverture += self.hookGenerator.callback(self.table.cadeau_recupere, (cadeau,))
            hooks.append(hook_ouverture)
            
            # Fermeture du bras
            hook_fermeture = self.hookGenerator.hook_position(cadeau["position"] + Point(sens * self.decalage_x_ferme, self.decalage_y_bord ), effectuer_symetrie=(self.config["couleur"] == "bleu"))
            hook_fermeture += self.hookGenerator.callback(self.robot.fermer_cadeau)
            hooks.append(hook_fermeture)

        # Déplacement le long de la table (peut être un peu trop loin ?)
        self.robot.va_au_point(self.info_versions[1-version]["point_entree"], hooks)
        
 
    def _termine(self):
        # Fermeture du bras (le dernier hook n'étant pas atteint)
        if self.robot.actionneur_cadeaux_sorti():
            #il faut définir une stratégie de sortie pour éviter d'endommager l'actionneur
            self.effectuer_symetrie = False
            if self.robot.x > 0:
                self.robot.tourner(math.pi/4)
            else:
                self.robot.tourner(-math.pi/4)
            self.robot.fermer_cadeau()

    def versions(self):
        self.decalage_x_ouvre = -50
        self.decalage_x_ferme = 200
        marge_au_bord = 50
        self.decalage_y_bord = self.config["rayon_robot"] + marge_au_bord
        self.decalage_x_pour_reglette_blanche = -100
        
        cadeaux = self.table.cadeaux_entrees()
        marche_arriere = self.config["couleur"] == "rouge"
        
        if cadeaux == []:
            return []
            
        point_entree_recherche_chemin = {}
        for cadeau in cadeaux:
            point_entree_recherche_chemin[cadeau["id"]] = cadeau["position"].copy()
            point_entree_recherche_chemin[cadeau["id"]].y += self.decalage_y_bord
            if cadeau["id"] == 0:
                #cadeau de notre côté : il faut se décaler vers le haut pour éviter la reglette
                point_entree_recherche_chemin[cadeau["id"]].x += self.decalage_x_pour_reglette_blanche
            
            ##DEBUG
            if self.config["couleur"] == "bleu":
                self.simulateur.drawPoint(-point_entree_recherche_chemin[cadeau["id"]].x,point_entree_recherche_chemin[cadeau["id"]].y, "blue")
            else:
                self.simulateur.drawPoint(point_entree_recherche_chemin[cadeau["id"]].x,point_entree_recherche_chemin[cadeau["id"]].y, "red")
            ##
            
        # S'il n'y a plus qu'un seul cadeau, cadeaux contient quand même deux éléments
        if cadeaux[0]["position"].x < cadeaux[1]["position"].x:
            self.info_versions = [
                {"point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[0]["id"]], "point_entree": cadeaux[0]["position"]+Point(1 * self.decalage_x_ouvre,self.decalage_y_bord), "sens": 1, "marche_arriere": not marche_arriere},               
                {"point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[1]["id"]], "point_entree": cadeaux[1]["position"]+Point(-1 * self.decalage_x_ouvre,self.decalage_y_bord), "sens": -1, "marche_arriere": marche_arriere}
            ]
        else:
            self.info_versions = [
                {"point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[0]["id"]], "point_entree": cadeaux[0]["position"]+Point(-1 * self.decalage_x_ouvre,self.decalage_y_bord), "sens": -1, "marche_arriere": marche_arriere},
                {"point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[1]["id"]], "point_entree": cadeaux[1]["position"]+Point(1 * self.decalage_x_ouvre,self.decalage_y_bord), "sens": 1, "marche_arriere": not marche_arriere}
            ]

        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
                
    def score(self):
        return 4 * len(self.table.cadeaux_restants())

    def poids(self):
        return 1

class ScriptRecupererVerres(Script):
        
    def _execute(self, version):
        
        # Désactivation de la symétrie
        self.robot.effectuer_symetrie = False
        
        # Point d'entrée du script
        entree = self._point_recuperation_verre(self.info_versions[version]["point_entree"])
        #self.robot.recherche_de_chemin(entree, False)
        
        # Récupération du premier verre, avec recherche de chemin
        self._recuperation_verre(self.info_versions[version]["verre_entree"])

        # Tant qu'il y a de la place dans le robot
        while self.robot.places_disponibles(True) != 0 or self.robot.places_disponibles(False) != 0:
            
            # Indentification du verre le plus proche dans la zone
            position = Point(self.robot.x, self.robot.y)
            verre = self.table.verre_le_plus_proche(position, self.zone)
            
            # Sortie du script si plus aucun verre
            if verre is None:
                break
            
            # Récupération du verre
            self._recuperation_verre(verre)
            
    def _recuperation_verre(self, verre):
        """
        Procédure de récupération d'un verre
        """
        avant = self._choix_ascenceur()
        self.robot.marche_arriere = not avant
        self.robot.va_au_point(verre["position"])
        self.robot.recuperer_verre(avant)
        self.table.verre_recupere(verre)
        
    def _choix_ascenceur(self):
        """
        Effectue le choix de l'ascenceur avant ou arrière
        """
        # Prend par l'avant par défaut, l'arrière s'il n'y a plus de places
        return self.robot.places_disponibles(True) != 0
            
    def _point_recuperation_verre(self, point):
        """
        Récupère le point de destination pour récupérer un verre
        S'appuie sur la position actuelle du robot
        """
        # Vecteur de direction du verre vers le robot
        direction = (Point(self.robot.x, self.robot.y) - point).unitaire()
        
        # Point de récupération (à déterminer)
        recuperation = point + 100 * direction
        
        return recuperation
         
    def _termine(self):
        pass
        
    @abc.abstractmethod
    def versions(self):
        """
        Récupération des versions du script.
        Doit être surchargé dans les 2 scripts enfants, un par couleur
        """
        # Récupération des verres d'entrées
        verres = self.table.verres_entrees(self.zone)
        
        # Plus aucun verre sur la table ou plus de place dans le robot
        if len(verres) == 0 or (self.robotVrai.places_disponibles(True) == 0 and self.robotVrai.places_disponibles(False) == 0):
            self.info_versions = []

        # Un seul verre
        elif len(verres) == 1:
            self.info_versions = [
                {"point_entree": verres[0]["position"], "verre_entree": verres[0]}
            ]
            
        # Cas général: plusieurs points d'entrées
        else:
            self.info_versions = [
                {"point_entree": verre["position"], "verre_entree": verre} for verre in verres
            ]
            
        return list(range(len(self.info_versions)))
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]

    def score(self):
        nb_verres_restants = len(self.table.verres_restants(self.zone))
        verres_stockable_avant = self.robotVrai.places_disponibles(True)
        verres_stockable_arriere = self.robotVrai.places_disponibles(False)
        
        # On calcule le nombre de verre qu'on pourra mettre à l'avant
        if nb_verres_restants > verres_stockable_avant:
            nb_verres_avant = verres_stockable_avant
        else:
            nb_verres_avant = nb_verres_restants

        # Puis le nombre qu'on pourra mettre à l'arrière
        if nb_verres_restants - nb_verres_avant > verres_stockable_arriere:
            nb_verres_arriere = verres_stockable_arriere
        else:
            nb_verres_arriere = nb_verres_restants - nb_verres_avant

        # Le nombre de points gagnés en remplissant l'ascenseur avant
        points_avant = 4*((self.robotVrai.nb_verres_avant + nb_verres_avant) * (self.robotVrai.nb_verres_avant + nb_verres_avant + 1) / 2 - (self.robotVrai.nb_verres_avant) * (self.robotVrai.nb_verres_avant + 1) / 2)

        # Le nombre de points gagnés en remplissant l'ascenseur arrière
        points_arriere = 4*((self.robotVrai.nb_verres_arriere + nb_verres_arriere) * (self.robotVrai.nb_verres_arriere + nb_verres_arriere + 1) / 2 - (self.robotVrai.nb_verres_arriere) * (self.robotVrai.nb_verres_arriere + 1) / 2)

        return points_avant + points_arriere

    def poids(self):
        return 1

class ScriptRecupererVerresZoneRouge(ScriptRecupererVerres):
    
    def __init__(self):
        self.zone = table.Table.ZONE_VERRE_ROUGE
        
    def versions(self):
        return super().versions()
        
        
class ScriptRecupererVerresZoneBleu(ScriptRecupererVerres):
    
    def __init__(self):
        self.zone = table.Table.ZONE_VERRE_BLEU
        
    def versions(self):
        return super().versions()
        
        
"""        
class ScriptCasserTour(Script):

    def versions(self):
        return []
        
    def point_entree(self, id_version):
        pass
        
    def score(self):
        pass

    def _execute(self, id_version):
        return (time()-self.timer.get_date_debut())    #à revoir

    def poids(self):
        return 1
        
class ScriptDeposerVerres(Script): #contenu pipeau
    
    def _execute(self):
        self.va_au_point(Point(1300,200))
        self.va_au_point(Point(1300,1800))

    def versions(self):
        return []
        
    def point_entree(self, id_version):
        pass

    def score(self):
        return 4*(self.robotVrai.nb_verres_avant*(self.robotVrai.nb_verres_avant+1)/2+self.robotVrai.nb_verres_arriere*(self.robotVrai.nb_verres_arriere+1)/2)

    def poids(self):
        return 1
"""
