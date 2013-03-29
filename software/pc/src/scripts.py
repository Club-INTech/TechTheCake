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
    def dependances(self, robot, robotChrono, hookGenerator, table, config, log):
        """
        Gère les services nécessaires aux scripts. On n'utilise pas de constructeur.
        """
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
            raise robot.ExceptionMouvementImpossible(self.robot)
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
    
    def __init__(self, robot, robotChrono, hookGenerator, table, config, log):
        self.log = log
        self.scripts = {}
        
        # Instanciation automatique des classes héritant de Script
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for nom, obj in classes:
            heritage = list(inspect.getmro(obj))
            if not inspect.isabstract(obj) and Script in heritage:
                self.scripts[nom] = obj()
                self.scripts[nom].dependances(robot, robotChrono, hookGenerator, table, config, log)
                if hasattr(self.scripts[nom], '_constructeur'): self.scripts[nom]._constructeur()

class ScriptBougies(Script):
   
    def _constructeur(self):
        """
        Permet de factoriser et de rendre visibles les différentes constantes et étalonnages du script.
        Les valeurs entières spécifiées ici sont en mm et sont à tester en pratique ! Les signes sont déjà implémentés. 
        """
        
        # Vrai si on n'a reçu aucune information de l'application android (sert au calcul des points)
        self.en_aveugle = False

        self.couleur_a_traiter = self.table.COULEUR_BOUGIE_ROUGE if self.config["couleur"] == "rouge" else self.table.COULEUR_BOUGIE_BLEU
        
        # pour calculer simplement les delta_angle
        rayon_bras = float(500 + self.config["distance_au_gateau"])
        
        # Prise en compte actionneur bas / haut
        self.delta_angle_actionneur_haut = -80 / rayon_bras # Actionneur haut à l'avant du robot
        self.delta_angle_actionneur_bas =   80 / rayon_bras # Actionneur bas à l'arrière du robot
        
        #constantes d'écart à la bougie (valeurs absolues)
        self.delta_abs_angle_baisser_bras = 15 / rayon_bras
        self.delta_abs_angle_lever_bras = 20 / rayon_bras
        
        # Ecart angulaire entre le point d'entrée et la bougie : tient compte du décalage des actionneurs.
        delta_actionneurs = max(abs(self.delta_angle_actionneur_haut), abs(self.delta_angle_actionneur_bas))
        self.delta_angle_entree = self.delta_abs_angle_baisser_bras + delta_actionneurs + 20/rayon_bras
        
        # Trouve l'angle du point_entree_recherche_chemin à partir des distances de sécurité choisies
        self.distance_entree    = self.config["distance_au_gateau"] + self.config["longueur_robot"]/2
        self.distance_entree_rc = self.config["distance_au_gateau"] + self.config["rayon_robot"]
        self.delta_angle_entree_rc = math.acos((500+self.distance_entree)/(500+self.distance_entree_rc))
        
        #angle maximal du point d'entrée pour ne pas toucher les bords de table
        self.angle_max = math.asin((self.config["rayon_robot"] + 10) / (500 + self.config["distance_au_gateau"] + self.config["longueur_robot"]/2))
        
    def _point_polaire(self, angle, distance_gateau):
        """
        Retourne le point sur la table correspondant à un angle de bougie
        """
        rayon = 500 + distance_gateau
        return Point(0, 2000) + Point(rayon * math.cos(angle), rayon * math.sin(angle))
        
    def versions(self):
        """
        Récupération des versions du script
        - [] si aucune bougie à valider
        - 2 versions sinon, où le gateau est parcouru dans un sens différent en validant toutes les bougies restantes
        """
        
        # Récupération des bougies restantes
        bougies = self.table.bougies_entrees(self.couleur_a_traiter)
        
        # Cas où toutes les bougies sont déjà validées
        if bougies == []:
            return []
        
        #position angulaire du point d'entrée
        angles_entree = [bougies[0]["position"] - self.delta_angle_entree, 
                         bougies[1]["position"] + self.delta_angle_entree ]
                         
        #on bride pour ne pas toucher les bords de table
        angles_entree = [max(min(-self.angle_max, angle), -math.pi+self.angle_max) for angle in angles_entree]
        
        #décalage angulaire pour les point_entree_recherche_chemin (le signe se dirige vers le centre de la table)
        deltas_angle_rc = [math.copysign(self.delta_angle_entree_rc,-(bougies[0]["position"]+math.pi/2)),
                           math.copysign(self.delta_angle_entree_rc,-(bougies[1]["position"]+math.pi/2)) ]
        
        # Cas où il reste au moins une bougie
        self.info_versions = [
            {
                "angle_entree": angles_entree[0],
                "point_entree": self._point_polaire(angles_entree[0], self.distance_entree),
                "point_entree_recherche_chemin": self._point_polaire(angles_entree[0] + deltas_angle_rc[0], self.distance_entree_rc),
                "marche_arriere": False,
                "sens": 1
            },               
            {
                "angle_entree": angles_entree[1],
                "point_entree": self._point_polaire(angles_entree[1], self.distance_entree),
                "point_entree_recherche_chemin": self._point_polaire(angles_entree[1] + deltas_angle_rc[1], self.distance_entree_rc),
                "marche_arriere": True,
                "sens": -1
            }
        ]
        
        return [0, 1]
        
    def _execute(self, version):

    
        
        self.robot.set_vitesse_translation(1)
        self.robot.set_vitesse_rotation(1)
        # Il n'y a aucune symétrie sur la couleur dans les déplacements
        self.robot.marche_arriere = False
        self.robot.effectuer_symetrie = False
        
        # Définition du parcours
        entree = self.info_versions[version]["point_entree"]
        sortie = self.info_versions[1-version]["point_entree"]
        vers_x_croissant = sortie.x > entree.x
        
        # Déplacement proche du point d'entrée avec recherche de chemin
        proche_entree = self.info_versions[version]["point_entree_recherche_chemin"]
        self.robot.recherche_de_chemin(proche_entree, recharger_table=False)
        
        # Déplacement au point d'entrée
        orientation_tangente = self.info_versions[version]["angle_entree"] + math.pi/2
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne=entree, orientation_finale_voulue=orientation_tangente)
        self.robot.va_au_point(entree)
        
        # Hooks sur chaque bougie à enfoncer
        hooks = []
        
        # Inversion du sens de parcours
        if vers_x_croissant:
            delta_angle_baisser_bras = - self.delta_abs_angle_baisser_bras
            delta_angle_lever_bras = self.delta_abs_angle_lever_bras
        else:
            delta_angle_baisser_bras = self.delta_abs_angle_baisser_bras
            delta_angle_lever_bras = - self.delta_abs_angle_lever_bras
            
        # Récupération des bougies restantes dans notre couleur
        for bougie in self.table.bougies_restantes(self.couleur_a_traiter):
            
            angle_baisser_bras = bougie["position"] + delta_angle_baisser_bras
            angle_lever_bras = bougie["position"] + delta_angle_lever_bras
            
            if bougie["enHaut"]:
                angle_baisser_bras += self.delta_angle_actionneur_haut
                angle_lever_bras += self.delta_angle_actionneur_haut
            else:
                angle_baisser_bras += self.delta_angle_actionneur_bas
                angle_lever_bras += self.delta_angle_actionneur_bas
                
            # Baisser le bras
            hook_baisser_bras = self.hookGenerator.hook_angle_gateau(angle_baisser_bras, vers_x_croissant)
            hook_baisser_bras += self.hookGenerator.callback(self.robot.traiter_bougie, (bougie["enHaut"],))
            hook_baisser_bras += self.hookGenerator.callback(self.table.bougie_recupere, (bougie,))
            hooks.append(hook_baisser_bras)
            
            # Lever le bras
            hook_baisser_bras = self.hookGenerator.hook_angle_gateau(angle_lever_bras, vers_x_croissant)
#            hook_baisser_bras += self.hookGenerator.callback(self.robot.initialiser_bras_bougie, (bougie["enHaut"],)) #Pourquoi n'en lever qu'un?!
            hook_baisser_bras += self.hookGenerator.callback(self.robot.initialiser_bras_bougie, (True,)) #Pourquoi n'en lever qu'un?!
            hook_baisser_bras += self.hookGenerator.callback(self.robot.initialiser_bras_bougie, (False,)) #Pourquoi n'en lever qu'un?!
            hooks.append(hook_baisser_bras)
        
        # Lancement de l'arc de cercle
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        self.robot.arc_de_cercle(sortie, hooks)
        
    def _termine(self):
        # Fermeture des actionneurs bougies : il faut enchainer ces actions pour se dégager du gateau.
        #TODO : trouver autre chose que les finally embriqués...
        
        orientation_normale = math.atan2(self.robot.y - 2000, self.robot.x - 0)
        distance_degagement = 2*self.config["rayon_robot"]
        
        if self.robot.actionneur_bougies_sorti():
            self.log.debug("Fin du script bougies : repli des actionneurs bougies.")
            self.effectuer_symetrie = False
            try:
                self.robot.tourner(orientation_normale + math.pi/2)
            finally:
                try:
                    #déplacement tangent au gateau : dégagement de l'obstacle vers le centre de la table
                    self.robot.avancer(-math.copysign(distance_degagement, self.robot.x))
                except robot.ExceptionMouvementImpossible:
                    # On ne peut pas : dégagement vers les bords
                    self.robot.avancer(math.copysign(distance_degagement, self.robot.x))
                finally:
                    try:
                        # Une rotation est plus sure pour ne pas endommager les actionneurs
                        orientation_normale = math.atan2(self.robot.y - 2000, self.robot.x - 0)
                        self.robot.tourner(orientation_normale)
                    finally:
                        self.robot.rentrer_bras_bougie()
        else:
            self.log.debug("Fin du script bougies : les actionneurs bougies sont déjà rentrés.")
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
        
    def score(self):
        if self.en_aveugle:
            return 2 * len([element for element in self.table.bougies_restantes(self.couleur_a_traiter)])
        else:
            return 4 * len([element for element in self.table.bougies_restantes(self.couleur_a_traiter)])
    
    def poids(self):
        return 1

class ScriptCadeaux(Script):
        
    def _execute(self, version):
        
        # Effectue une symétrie sur tous les déplacements
        self.robot.effectuer_symetrie = False
        
        # Déplacement proche du point d'entrée avec recherche de chemin
        self.robot.marche_arriere = False
        self.robot.set_vitesse_translation(140)
        self.robot.set_vitesse_rotation(150)
        self.robot.recherche_de_chemin(self.info_versions[version]["point_entree_recherche_chemin"], recharger_table=False)
        
        # Déplacement au point d'entrée
        point_entree = self.info_versions[version]["point_entree"]
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne=point_entree, orientation_finale_voulue=0)
        self.robot.va_au_point(point_entree)

        # Orientation du robot
        sens = self.info_versions[version]["sens"]
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        
        # Création des hooks pour tous les cadeaux à activer
        hooks = []
        # Ouverture du bras en face du cadeau
        for cadeau in self.table.cadeaux_restants():
            hook_ouverture = self.hookGenerator.hook_position(cadeau["position"] + Point(sens * self.decalage_x_ouvre, self.decalage_y_bord ), tolerance_mm=35, effectuer_symetrie=False)
            hook_ouverture += self.hookGenerator.callback(self.robot.ouvrir_cadeau)
            hook_ouverture += self.hookGenerator.callback(self.table.cadeau_recupere, (cadeau,))
            hooks.append(hook_ouverture)
            
        # Fermeture du bras pendant les "trous" entre cadeaux
        for trou in self.table.trous_cadeaux:
            hook_fermeture = self.hookGenerator.hook_position(trou + Point(sens * self.decalage_x_ferme, self.decalage_y_bord ), tolerance_mm=35, effectuer_symetrie=False)
            hook_fermeture += self.hookGenerator.callback(self.robot.fermer_cadeau)
            hooks.append(hook_fermeture)

        # Déplacement le long de la table (peut être un peu trop loin ?)
        self.robot.set_vitesse_translation(100)
        self.robot.va_au_point(self.info_versions[1-version]["point_entree"], hooks)
        
 
    def _termine(self):
        # Fermeture du bras (le dernier hook n'étant pas atteint)
        if self.robot.actionneur_cadeaux_sorti():
            self.log.debug("Fin du script cadeau : repli de l'actionneur cadeaux.")
            self.effectuer_symetrie = False
            try:
                angle_repli = math.pi/3
                if self.robot.x > 0:
                    self.robot.tourner(angle_repli)
                else:
                    self.robot.tourner(-angle_repli)
            finally:
                self.robot.fermer_cadeau()
        else:
            self.log.debug("Fin du script cadeau : l'actionneur cadeaux est déjà rentré.")

    def versions(self):
        self.decalage_x_ouvre = -50
        self.decalage_x_ferme = -60#350
        self.decalage_y_bord = self.config["rayon_robot"] + 100
        self.decalage_x_pour_reglette_blanche = 100
        
        cadeaux = self.table.cadeaux_entrees()
        
        if cadeaux == []:
            return []
            
        point_entree_recherche_chemin = {}
        for cadeau in cadeaux:
            point_entree_recherche_chemin[cadeau["id"]] = cadeau["position"].copy()
            point_entree_recherche_chemin[cadeau["id"]].y += self.decalage_y_bord
            #cadeau de notre côté : il faut se décaler vers le haut pour éviter la reglette
            if cadeau["id"] == 0:
                point_entree_recherche_chemin[cadeau["id"]].x += self.decalage_x_pour_reglette_blanche
            elif cadeau["id"] == 7:
                point_entree_recherche_chemin[cadeau["id"]].x -= self.decalage_x_pour_reglette_blanche
            
        # S'il n'y a plus qu'un seul cadeau, cadeaux contient quand même deux éléments
        self.info_versions = [
            {   "point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[0]["id"]], 
                "point_entree": cadeaux[0]["position"] + Point(1 * self.decalage_x_ouvre,self.decalage_y_bord), 
                "sens": 1, 
                "marche_arriere": False
            },               
            {   "point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[1]["id"]], 
                "point_entree": cadeaux[1]["position"] + Point(-1 * self.decalage_x_ouvre,self.decalage_y_bord), 
                "sens": -1, 
                "marche_arriere": True
            }]
        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
                
    def score(self):
        return 4 * len(self.table.cadeaux_restants())

    def poids(self):
        return 1

class ScriptRecupererVerres(Script):
        
    def _constructeur(self):
        self.marge_recuperation = 100
        
    def _execute(self, version):
        
        # Désactivation de la symétrie
        self.robot.effectuer_symetrie = False
        
        # Point d'entrée du script par recherche de chemin
        premier_verre = self.info_versions[version]["point_entree"]
        chemin_vers_entree = self.robot.recherche_de_chemin(premier_verre, recharger_table=False, renvoie_juste_chemin=True)
        
        #suppression du point d'arrivé (le verre) qui est remplacé par un point suffisament éloigné, sur le dernier segment du chemin
        if len(chemin_vers_entree) > 2 and chemin_vers_entree[-1].distance(chemin_vers_entree[-2]) < self.marge_recuperation:
            #cette optimisation fonctionnerait mal sur les segments plus courts que la marge de récupération
            del chemin_vers_entree[-1]
        del chemin_vers_entree[-1]
        chemin_avec_depart = [Point(self.robot.x,self.robot.y)]+chemin_vers_entree
        nouvelle_destination = self._point_recuperation_verre(premier_verre, chemin_avec_depart[-1])
        chemin_vers_entree.append(nouvelle_destination)
        
        self.robot.suit_chemin(chemin_vers_entree, symetrie_effectuee=True)
        
        # Récupération du premier verre
        self._recuperation_verre(self.info_versions[version]["verre_entree"])

        # Tant qu'il y a de la place dans le robot
        #TODO : dangereux si bouclage entre 2 verres inaccesibles. Prévoir un timeout ?
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
        destination = self._point_recuperation_verre(verre["position"])
        mieux_en_arriere = self.robot.marche_arriere_est_plus_rapide(destination)
        if self.robot.places_disponibles(not mieux_en_arriere):
            self.robot.marche_arriere = mieux_en_arriere
        else:
            self.robot.marche_arriere = not mieux_en_arriere
        
        self.robot.va_au_point(destination)
        self.robot.recuperer_verre(not self.robot.marche_arriere)
        self.table.verre_recupere(verre)
        
    def _point_recuperation_verre(self, pos_verre, pos_robot=None):
        """
        Récupère le point de destination pour récupérer un verre
        S'appuie sur la position actuelle du robot
        """
        #on peut indiquer en paramètre la position du robot à la fin d'un trajet
        if pos_robot is None:
            pos_robot = Point(self.robot.x, self.robot.y)
            
        # Vecteur de direction du verre vers le robot
        direction = (pos_robot - pos_verre).unitaire()
        
        # Point de récupération (à déterminer)
        recuperation = pos_verre + self.marge_recuperation * direction
        
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
