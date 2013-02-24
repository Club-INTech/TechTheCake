from time import sleep,time
from outils_maths.point import Point
import math
import unittest
import abc

"""

Règles concernant l'écriture de scripts:

- On considère dans tous les scripts qu'on est ROUGE.
- On peut utilier les méthodes de robot pour gérer la symétrie (robot.effectuer_symetrie) ou la marche arrière (robot.marche_arriere)

"""

class Script(metaclass=abc.ABCMeta):
    """
    classe mère des scripts
    se charge des dépendances
    """
    def dependances(self, config, log, robot, robotChrono, hookGenerator, rechercheChemin, table, simulateur):
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
        self.simulateur = simulateur
        
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

    def agit(self, params):
        """
        L'appel script.agit() effectue vraiment les instructions contenues dans _execute().
        Les paramètres de agit() sont les mêmes que ceux envoyés à _execute()
        """
        self.robot = self.robotVrai
        if type(params) is tuple:
            self._execute(*params)
        elif params is None:
            self._execute()
        else:
            self._execute(params)
        
    def calcule(self, params):
        """
        L'appel script.calcule() retourne la durée estimée des actions contenues dans executer().
        """
        self.robot = self.robotChrono
        self.robot.reset_compteur()
        self.robot.maj_x_y_o(self.robotVrai.x, self.robotVrai.y, self.robotVrai.orientation)
        if type(params) is tuple:
            self._execute(*params)
        elif params is None:
            self._execute()
        else:
            self._execute(params)
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
    def _execute(self, id_version):
        pass

             
class ScriptManager:
    
    def __init__(self, config, log, robot, robotChrono, hookGenerator, rechercheChemin, table, simulateur):
        import inspect, sys
        self.log = log
        self.scripts = {}
        
        # Instanciation automatique des classes héritant de Script
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for nom, obj in classes:
            heritage = list(inspect.getmro(obj))
            if Script in heritage and obj != Script:
                print(nom)
                self.scripts[nom] = obj()
                self.scripts[nom].dependances(config, log, robot, robotChrono, hookGenerator, rechercheChemin, table, simulateur)

class ScriptBougies(Script):
   
    def _execute(self, version):

        # Il n'y a aucune symétrie sur la couleur dans les déplacements
        self.robot.effectuer_symetrie = False
        
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
            point_baisser_bras = self._correspondance_point_angle(bougie["position"] + delta_angle_baisser_bras)
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
        self.robot.arc_de_cercle(sortie.x, sortie.y, hooks)
        
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
    def _correspondance_point_angle(self, angle):
        """
        Retourne le point sur la table correspondant à un angle de bougie
        """
        rayon = 500 + self.config["distance_au_gateau"] + self.config["longueur_robot"] / 2
        return Point(0, 2000) - Point(rayon * math.cos(angle), rayon * math.sin(angle))

    def versions(self):
        """
        Récupération des versions du script
        - [] si aucune bougie à valider
        - 2 versions sinon, où le gateau est parcouru dans un sens différent en validant toutes les bougies restantes
        """
        # Récupération des bougies restantes
        self.couleur_a_traiter = self.table.COULEUR_BOUGIE_ROUGE if self.config["couleur"] == "rouge" else self.table.COULEUR_BOUGIE_BLEU
        bougies = self.table.bougies_entrees()
        
        # Cas où toutes les bougies sont déjà validées
        if bougies == []:
            return []
            
        # Cas où il reste au moins une bougie
        delta_angle = -20 / float(500 + self.config["distance_au_gateau"])
        self.info_versions = [
            {
                "angle_entree": bougies[0]["position"] - delta_angle,
                "point_entree": self._correspondance_point_angle(bougies[0]["position"] - delta_angle),
                "marche_arriere": True,
                "sens": 1
            },               
            {
                "angle_entree": bougies[1]["position"] + delta_angle,
                "point_entree": self._correspondance_point_angle(bougies[1]["position"] + delta_angle),
                "marche_arriere": False,
                "sens": -1
            }
        ]
        
        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
        
    def score(self):
        point=0
        for element in self.table.bougies:
            if not element["couleur"]=="red" and not element["traitee"]: #la condition sur la couleur est pipeau
                point+=4
        return point
    
class ScriptCadeaux(Script):
        
    def _execute(self, version):

        sens = self.info_versions[version]["sens"]
        self.robot.va_au_point(self.info_versions[version]["point_entree"])
        
        # Orientation du robot
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        self.robot.effectuer_symetrie = True

        # Création des hooks pour tous les cadeaux à activer
        hooks = []
        for cadeau in self.table.cadeaux_restants():
            
            # Ouverture du bras
            hook_ouverture = self.hookGenerator.hook_position(cadeau["position"] + Point(sens * -50, 250))
            hook_ouverture += self.hookGenerator.callback(self.robot.ouvrir_cadeau)
            hook_ouverture += self.hookGenerator.callback(self.table.cadeau_recupere, (cadeau,))
            hooks.append(hook_ouverture)
            
            # Fermeture du bras
            hook_fermeture = self.hookGenerator.hook_position(cadeau["position"] + Point(sens * 200, 250))
            hook_fermeture += self.hookGenerator.callback(self.robot.fermer_cadeau)
            hooks.append(hook_fermeture)

        # La dernière fermeture du bras n'est pas attachée à une position
        hooks.pop()

        # Déplacement le long de la table
        self.robot.va_au_point(self.info_versions[1-version]["point_entree"], hooks)
        self.robot.tourner(math.pi / 2)
        self.robot.fermer_cadeau()

    def versions(self):
        self.decalage_gauche = Point(-100,250)
        self.decalage_droit = Point(100,250)
        
        cadeaux = self.table.cadeaux_entrees()
        marche_arriere = self.config["couleur"] == "rouge"
        
        if cadeaux == []:
            return []

        # S'il n'y a plus qu'un seul cadeau, cadeaux contient quand même deux éléments
        elif cadeaux[0]["position"].x < cadeaux[1]["position"].x:
            self.info_versions = [
                {"point_entree": cadeaux[0]["position"]+self.decalage_gauche, "sens": 1, "marche_arriere": not marche_arriere},               
                {"point_entree": cadeaux[1]["position"]+self.decalage_droit, "sens": -1, "marche_arriere": marche_arriere}
            ]
        else:
            self.info_versions = [
                {"point_entree": cadeaux[0]["position"]+self.decalage_droit, "sens": -1, "marche_arriere": marche_arriere},
                {"point_entree": cadeaux[1]["position"]+self.decalage_gauche, "sens": 1, "marche_arriere": not marche_arriere}
            ]

        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
                
    def score(self):
        return 4 * len(self.table.cadeaux_restants())

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
        
class ScriptDeposerVerres(Script): #contenu pipeau
    
    def _execute(self):
        self.va_au_point(Point(1300,200))
        self.va_au_point(Point(1300,1800))

    def versions(self):
        return []
        
    def point_entree(self, id_version):
        pass

    def score(self):
        return 4*max(self.robotVrai.nb_verres_avant*(self.robotVrai.nb_verres_avant+1)/2,self.robotVrai.nb_verres_arriere*(self.robotVrai.nb_verres_arriere+1)/2)


class ScriptRecupererVerres(Script): #contenu pipeau
    
    def _execute(self):
        self.va_au_point(Point(1300,200))
        self.va_au_point(Point(1300,1800))

    def versions(self):
        return []
        
    def point_entree(self, id_version):
        pass

    def score(self):
        point=0
        for element in self.table.verres:
            if element["present"]:       #à pondérer si l'ascenseur est plutôt plein ou plutôt vide
                point+=6 #à tirer vers le haut pour les faire en début de partie (et ensuite baisser les points par incertitude?)
"""

