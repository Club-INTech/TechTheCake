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
    def dependances(self, robot, robotChrono, hookGenerator, table, config, log, timer):
        """
        Gère les services nécessaires aux scripts. On n'utilise pas de constructeur.
        """
        self.robotVrai = robot
        self.robotChrono = robotChrono
        self.hookGenerator = hookGenerator
        self.table = table
        self.config = config
        self.log = log
        self.timer = timer

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
    def poids(self, t):
        pass

             
class ScriptManager:
    
    def __init__(self, robot, robotChrono, hookGenerator, table, config, log, timer):
        self.log = log
        self.scripts = {}
        
        # Instanciation automatique des classes héritant de Script
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for nom, obj in classes:
            heritage = list(inspect.getmro(obj))
            if not inspect.isabstract(obj) and Script in heritage:
                self.scripts[nom] = obj()
                self.scripts[nom].dependances(robot, robotChrono, hookGenerator, table, config, log, timer)
                if hasattr(self.scripts[nom], '_constructeur'): self.scripts[nom]._constructeur()

class ScriptBougies(Script):
   
    def _constructeur(self):
        """
        Permet de factoriser et de rendre visibles les différentes constantes et étalonnages du script.
        Les valeurs entières spécifiées ici sont en mm et sont à tester en pratique ! Les signes sont déjà implémentés. 
        """
        
        # Vrai si on n'a reçu aucune information de l'application android (sert au calcul des points)
        self.en_aveugle = False
        self.malus = 0
        
        self.couleur_a_traiter = self.table.COULEUR_BOUGIE_ROUGE | self.table.COULEUR_BOUGIE_BLANC if self.config["couleur"] == "rouge" else self.table.COULEUR_BOUGIE_BLEU | self.table.COULEUR_BOUGIE_BLANC
        
        # pour calculer simplement les delta_angle
        rayon_bras = float(500 + self.config["distance_au_gateau"])
        
        # Prise en compte actionneur bas / haut
        self.delta_angle_actionneur_haut = 80 / rayon_bras # Actionneur haut à l'avant du robot
        self.delta_angle_actionneur_bas =  -22 / rayon_bras # Actionneur bas à l'arrière du robot
        
        #constantes d'écart à la bougie (valeurs absolues)
        self.delta_abs_angle_baisser_bras = 15 / rayon_bras
        self.delta_abs_angle_lever_bras = 20 / rayon_bras
        
        #correction pour l'asymétrique du parcours vers x croissants
        self.correction_vers_x_croissants = 20 / rayon_bras
        
        # Ecart angulaire entre le point d'entrée et la bougie : tient compte du décalage des actionneurs.
        delta_actionneurs = max(abs(self.delta_angle_actionneur_haut), abs(self.delta_angle_actionneur_bas))
        self.delta_angle_entree = self.delta_abs_angle_baisser_bras + delta_actionneurs + 20/rayon_bras
        
        # Trouve l'angle du point_entree_recherche_chemin à partir des distances de sécurité choisies
        self.distance_entree    = self.config["distance_au_gateau"] + self.config["longueur_robot"]/2
        self.distance_entree_rc = self.config["distance_au_gateau"] + self.config["rayon_robot"]
        self.delta_angle_entree_rc = math.acos((500+self.distance_entree)/(500+self.distance_entree_rc))
        
        #angle maximal du point d'entrée pour ne pas toucher les bords de table
        self.angle_max = math.asin((self.config["rayon_robot"] - 10) / (500 + self.config["distance_au_gateau"] + self.config["longueur_robot"]/2))
        
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
                "bougie_entree": bougies[0],
                "point_entree": self._point_polaire(angles_entree[0], self.distance_entree),
                "point_entree_recherche_chemin": self._point_polaire(angles_entree[0] + deltas_angle_rc[0], self.distance_entree_rc),
                "marche_arriere": False,
                "sens": 1
            },               
            {
                "angle_entree": angles_entree[1],
                "bougie_entree": bougies[1],
                "point_entree": self._point_polaire(angles_entree[1], self.distance_entree),
                "point_entree_recherche_chemin": self._point_polaire(angles_entree[1] + deltas_angle_rc[1], self.distance_entree_rc),
                "marche_arriere": True,
                "sens": -1
            }
        ]
        
        return [0, 1]
        
    def _execute(self, version):
        
        self.robot.set_vitesse_translation("entre_scripts")
        self.robot.set_vitesse_rotation("entre_scripts")
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

        # Initialisation des deux bras
        self.robot.actionneurs_bougie(True, "haut")
        self.robot.actionneurs_bougie(False, "haut")
        
        # Déplacement au point d'entrée
        self.robot.set_vitesse_translation("proche_gateau")
        self.robot.set_vitesse_rotation("proche_gateau")
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
                
            if vers_x_croissant:
                #négatif = comme actionneur bas = en avant
                angle_baisser_bras -= self.correction_vers_x_croissants
                angle_lever_bras -= self.correction_vers_x_croissants
            
            # Baisser le bras
            hook_baisser_bras = self.hookGenerator.hook_angle_gateau(angle_baisser_bras, vers_x_croissant)
            hook_baisser_bras += self.hookGenerator.callback(self.robot.actionneurs_bougie, (bougie["enHaut"],"moyen"))
            hook_baisser_bras += self.hookGenerator.callback(self.table.bougie_recupere, (bougie,))
            hooks.append(hook_baisser_bras)
            
            # Lever le bras (On relève seulement celui qui a été abaissé)
            hook_lever_bras = self.hookGenerator.hook_angle_gateau(angle_lever_bras, vers_x_croissant)
            hook_lever_bras += self.hookGenerator.callback(self.robot.actionneurs_bougie, (bougie["enHaut"],"haut"))
            hooks.append(hook_lever_bras)
        
        self.bougies_extremales(self.info_versions[version]["bougie_entree"])
            
        # Lancement de l'arc de cercle
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        self.robot.arc_de_cercle(sortie, hooks)
        
        self.bougies_extremales(self.info_versions[1-version]["bougie_entree"])
        
    def bougies_extremales(self, bougie_entree):
                
        #on enfonce les bougies extremales si possible (l'actionneur du haut pour celle des x petits, celui du bas pour x grands)
        if bougie_entree["id"] == 1 and self.table.bougies[1]["couleur"] & self.couleur_a_traiter:
            self.robot.tourner(-1.4)
            self.robot.actionneurs_bougie(True, "moyen")
            sleep(0.3)
            self.robot.actionneurs_bougie(True, "haut")
        elif bougie_entree["id"] == 19 and self.table.bougies[19]["couleur"] & self.couleur_a_traiter:
            self.robot.tourner(1.2)
            self.robot.actionneurs_bougie(False, "moyen")
            self.robot.actionneurs_bougie(True, "moyen")
            sleep(0.3)
            self.robot.actionneurs_bougie(False, "haut")
            self.robot.actionneurs_bougie(True, "haut")
            
    def _termine(self):
        # Fermeture des actionneurs bougies : il faut enchainer ces actions pour se dégager du gateau.
        #TODO : trouver autre chose que les finally embriqués...
        
        orientation_normale = math.atan2(self.robot.y - 2000, self.robot.x - 0)
        distance_degagement = 2*self.config["rayon_robot"]
        
        self.robot.set_vitesse_translation("proche_gateau")
        self.robot.set_vitesse_rotation("proche_gateau")
        
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
                        self.robot.actionneurs_bougie(True, "bas")
                        self.robot.actionneurs_bougie(False, "bas")
        else:
            self.log.debug("Fin du script bougies : les actionneurs bougies sont déjà rentrés.")
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
        
    def score(self):
        if self.en_aveugle:
            return 2 * len([element for element in self.table.bougies_restantes(self.couleur_a_traiter)])
        else:
            return 4 * len([element for element in self.table.bougies_restantes(self.couleur_a_traiter)])
    
    def poids(self, t):
        return -500 #Equivaut à une désactivation du script
        return self.malus

class ScriptCadeaux(Script):
        
    def _execute(self, version):
        
        # Effectue une symétrie sur tous les déplacements
        self.robot.effectuer_symetrie = False
        
        # Déplacement proche du point d'entrée avec recherche de chemin
        self.robot.marche_arriere = False
        self.robot.set_vitesse_translation("entre_scripts")
        self.robot.set_vitesse_rotation("entre_scripts")
        self.robot.recherche_de_chemin(self.info_versions[version]["point_entree_recherche_chemin"], recharger_table=False)
        
        # Déplacement au point d'entrée
        self.robot.set_vitesse_translation("prudence_reglette")
        self.robot.set_vitesse_rotation("prudence_reglette")
        point_entree = self.info_versions[version]["point_entree"]
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne=point_entree, orientation_finale_voulue=0)
        self.robot.va_au_point(point_entree)

        # Orientation du robot
        sens = self.info_versions[version]["sens"]
        self.robot.marche_arriere = self.info_versions[version]["marche_arriere"]
        
        #pour se réorienter
        avance_vers_x_croissant = not (1-version == self.robot.marche_arriere)
        self.robot.tourner(0 if avance_vers_x_croissant else math.pi)
        
        #ouverture du premier cadeau
        self.robot.actionneur_cadeau("haut")
        if self.robot is self.robotVrai: self.table.cadeau_recupere(self.table.cadeaux_entrees()[version])
        sleep(0.3)
        
        # Création des hooks pour tous les autres cadeaux à activer
        hooks = []
        
        # Ouverture du bras en face du cadeau
        for cadeau in self.table.cadeaux_restants():
            hook_ouverture = self.hookGenerator.hook_droite_verticale(cadeau["position"].x + sens * self.decalage_x_ouvre, vers_x_croissant=1-version)
            hook_ouverture += self.hookGenerator.callback(self.robot.actionneur_cadeau, ("haut",))
            hook_ouverture += self.hookGenerator.callback(self.table.cadeau_recupere, (cadeau,))
            hooks.append(hook_ouverture)

        # Fermeture du bras pendant les "trous" entre cadeaux
        for trou in self.table.trous_cadeaux:
            hook_fermeture = self.hookGenerator.hook_droite_verticale(trou.x + sens * self.decalage_x_ferme, vers_x_croissant=1-version)
            hook_fermeture += self.hookGenerator.callback(self.robot.actionneur_cadeau, ("moyen", ))
            hook_fermeture += self.hookGenerator.callback(self.robot.correction_angle, (0 if avance_vers_x_croissant else math.pi, ))
            hooks.append(hook_fermeture)

        # Déplacement le long de la table (peut être un peu trop loin ?)
        self.robot.set_vitesse_translation("cadeaux")
        self.robot.set_vitesse_rotation("cadeaux")
        point_sortie = Point(self.info_versions[1-version]["point_entree"].x, self.info_versions[version]["point_entree"].y)
        
        self.robot.va_au_point(point_sortie, hooks)
        
 
    def _termine(self):
        # Fermeture du bras (le dernier hook n'étant pas atteint)
        if self.robot.actionneur_cadeaux_sorti():
            self.log.debug("Fin du script cadeau : repli de l'actionneur cadeaux.")
            self.effectuer_symetrie = False
            try:
                angle_repli = math.pi/2
                if self.robot.x > 0:
                    self.robot.tourner(angle_repli)
                else:
                    self.robot.tourner(-angle_repli)
            finally:
                self.robot.actionneur_cadeau("bas")
        else:
            self.log.debug("Fin du script cadeau : l'actionneur cadeaux est déjà rentré.")

    def versions(self):
        self.decalage_x_ouvre = -160
        self.decalage_x_ferme = -230#350
        self.decalage_y_bord = self.config["rayon_robot"] + 65#90
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
        # Le coefficient 1/2 devant self.decalage_x_ouvre vient du fait qu'au début du script, la vitesse est encore faible et donc on doit moins anticiper les mouvements
        self.info_versions = [
            {   "point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[0]["id"]], 
                "point_entree": cadeaux[0]["position"] + Point(0,self.decalage_y_bord), 
                "sens": 1, 
                "marche_arriere": False
            },               
            {   "point_entree_recherche_chemin": point_entree_recherche_chemin[cadeaux[1]["id"]], 
                "point_entree": cadeaux[1]["position"] + Point(0,self.decalage_y_bord), 
                "sens": -1, 
                "marche_arriere": True
            }]
        return [0, 1]
        
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]
                
    def score(self):
        return 4 * len(self.table.cadeaux_restants())

    def poids(self, t):
        return 0

class ScriptRecupererVerres(Script):
        
    def _constructeur(self):
        # On va un peu trop loin afin de bien caler le verre au fond de l'ascenseur et lui permettre d'appuyer sur l'interrupteur
        self.marge_recuperation = -20
        self.marge_apres_chemin = self.marge_recuperation + 300
        
    def _execute(self, version):
        
        # Désactivation de la symétrie
        self.robot.effectuer_symetrie = False

        # On prend le premier verre dans le bon sens
        self.change = False

        # Point d'entrée du script par recherche de chemin
        premier_verre = self.info_versions[version]["point_entree"]
        chemin_vers_entree = self.robot.recherche_de_chemin(premier_verre, recharger_table=False, renvoie_juste_chemin=True)
        
        #suppression du point d'arrivé (le verre) qui est remplacé par un point suffisament éloigné, sur le dernier segment du chemin
        if len(chemin_vers_entree) > 2 and chemin_vers_entree[-1].distance(chemin_vers_entree[-2]) < self.marge_recuperation:
            #cette optimisation fonctionnerait mal sur les segments plus courts que la marge de récupération
            del chemin_vers_entree[-1]
        del chemin_vers_entree[-1]
        chemin_avec_depart = [Point(self.robot.x,self.robot.y)]+chemin_vers_entree
        nouvelle_destination = self._point_devant_verre(premier_verre, self.marge_apres_chemin, chemin_avec_depart[-1])
        chemin_vers_entree.append(nouvelle_destination)
        
        self.robot.set_vitesse_translation("entre_scripts")
        self.robot.set_vitesse_rotation("entre_scripts")
        self.robot.suit_chemin(chemin_vers_entree, symetrie_effectuee=True)
        
        # Récupération du premier verre
        self._recuperation_verre(self.info_versions[version]["verre_entree"])

        # Tant qu'il y a de la place dans le robot
        #TODO : dangereux si bouclage entre 2 verres inaccessibles. Prévoir un timeout ? (normalement OK)
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
        destination = self._point_devant_verre(verre["position"], self.marge_recuperation)

        # On remplit un ascenseur puis l'autre si tout se passe bien. Mais si un verre est absent, on change de côté (un ascenseur peut s'être bloqué trop bas)
        self.robot.marche_arriere = not self.robot.places_disponibles(True)
        if self.change:
            self.robot.marche_arriere = not self.robot.marche_arriere

#        self.robot.marche_arriere = self.robot.places_disponibles(False)

        # Code pour aller au plus rapide; alterne intelligement ascenseur avant et arrière
#        mieux_en_arriere = self.robot.marche_arriere_est_plus_rapide(destination)
#        if self.robot.places_disponibles(not mieux_en_arriere):
#            self.robot.marche_arriere = mieux_en_arriere
#        else:
#            self.robot.marche_arriere = not mieux_en_arriere

        # On est à distance.L'ascenseur est déjà levé. On s'avance jusqu'à positionner le verre sous l'ascenseur. Si le verre est présent, on ouvre l'ascenseur, on le descend, on le ferme et on le remonte. Si le verre est absent, on laisse l'ascenseur en haut.
        hooks = []

        hook_verre = self.hookGenerator.hook_capteur_verres(self.robot, not self.robot.marche_arriere)
        hook_verre += self.hookGenerator.callback(self.robot.stopper, (False,))
        hook_verre += self.hookGenerator.callback(self.robot.recuperer_verre, (not self.robot.marche_arriere, ))
        
        hooks.append(hook_verre)
        
        self.robot.set_vitesse_translation("recherche_verre")
        self.robot.set_vitesse_rotation("recherche_verre")

        self.robot.altitude_ascenseur(not self.robot.marche_arriere, "haut")

        # Sauvegarde de la place disponible afin de savoir si le verre a été pris ou non
        place_dispo_sauv = self.robotVrai.places_disponibles(not self.robot.marche_arriere)

        self.robot.va_au_point(destination, hooks)

        # Si le nombre de verre n'a pas changé c'est qu'on en a pas pris. On réagit donc en changeant d'ascenseur
        if self.robotVrai.places_disponibles(not self.robot.marche_arriere) == place_dispo_sauv and self.robot == self.robotVrai:
            # On ne change de côté que si c'est possible bien sûr, c'est-à-dire s'il y a de la place dans l'autre
            if self.robotVrai.places_disponibles(self.robot.marche_arriere) != 0:
                self.log.warning("Verre absent: on change d'ascenseur.")
                self.change = not self.change # BASCUUUULE !!!
            else:
                self.log.warning("Verre absent: pas de changement d'ascenseur possible.")

        # Dans tous les cas, que le verre ait été là ou non, on retire le verre de la table
        self.table.verre_recupere(verre)
        
    def _point_devant_verre(self, pos_verre, marge, pos_robot=None):
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
        recuperation = pos_verre + marge * direction
        
        return recuperation
         
    def _termine(self):
        # On descend les deux ascenseurs (ce qui réactive aussi les capteurs)
        self.robot.altitude_ascenseur(True, "plein")
        self.robot.altitude_ascenseur(False, "plein")

        
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

    def _nb_points(self, nb_verres_avant, nb_verres_arriere):
        return 4 * ( sum(range(1,nb_verres_avant+1)) + sum(range(1,nb_verres_arriere+1)) )
        
    def score(self):
        nb_verres_restants = len(self.table.verres_restants(self.zone))
        verres_stockable_avant = self.robotVrai.places_disponibles(True)
        verres_stockable_arriere = self.robotVrai.places_disponibles(False)
        
        # On calcule le nombre de verre qu'on gagnerait
        nb_en_plus_avant = min(verres_stockable_avant, nb_verres_restants)
        nb_en_plus_arriere = min(verres_stockable_arriere, nb_verres_restants - nb_en_plus_avant)

        points_avant_script = self._nb_points(self.robotVrai.nb_verres_avant, self.robotVrai.nb_verres_arriere)
        points_total = self._nb_points(self.robotVrai.nb_verres_avant + nb_en_plus_avant, self.robotVrai.nb_verres_arriere + nb_en_plus_arriere)
        
        return points_total - points_avant_script

    def poids(self, t):
        #ce calcul n'a pas de sens si aucune place n'est disponible
        if not (self.robotVrai.places_disponibles(True) or self.robotVrai.places_disponibles(False)):
            return 0
        
        #on calcule ici une valuation supplémentaire en fonction de l'avancée du match        
        if self.config["ennemi_prend_ses_verres"]:
            #formule fortement dégressive, qui pousse à prendre les verres au début, et décourage passé 20 sec 
            if t<45: return 0.0256*t**2 - 2.447*t + 40
            else: return -20 #attention à la parabole qui remonte...
            
        else:
            #formule faiblement décroissante, et linéaire (l'adverse peut foncer dans ses verres de facon aléatoire, donc indépendant de t)
            return max(0, 30 - 0.5*t)
        
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
        
        
class ScriptDeposerVerres(Script):
    
    def _constructeur(self):
        
        #position relative du point_entree_recherche_chemin par rapport au point_entree
        self.decalage_recherche_chemin = Point(-400,0)
        
        #recul à chaque nouveau dépot, pour éviter de dégommer les anciennes piles
        self.largeur_recul_piles = 170
        
        #distance entre le point d'entree et l'endroit où on dépose une pile
        self.distance_entree_depot = 120
        
    def versions(self):
        """
        L'idée, c'est que les assiettes nous obligent à déposer les piles de verres là où nos robots ont démarré. 
        Les cases au extrémités (1 et 5) permettent de déposer les verres sur une reglette en bois.
        """
        
        # Si on ne transporte aucun verre, aucune version
        if not self.robotVrai.deposer_verre_avant and not self.robotVrai.deposer_verre_arriere:
            return []

        #décalage dû aux reglettes
        decalages_reglettes = [Point(0,0), Point(0,0)]
        configs = [self.config["case_depart_principal"], self.config["case_depart_secondaire"]]
        for i in range(len(configs)):
            if configs[i] == 1:
                decalages_reglettes[i].y += 130
                decalages_reglettes[i].x -= 100
            elif configs[i] == 5:
                decalages_reglettes[i].y -= 130
                decalages_reglettes[i].x -= 100
                
        #case de départ du robot principal
        case_r1 = self.table.cases_depart[self.config["case_depart_principal"]-1]
        self.info_versions = [{   
                "point_entree_recherche_chemin": case_r1["centre"] + self.decalage_recherche_chemin,
                "point_entree": case_r1["centre"] + decalages_reglettes[0] + Point(-self.largeur_recul_piles*case_r1["nb_depots"],0),
                "id_case": self.config["case_depart_principal"]
            }]
                
        if self.config["case_depart_secondaire"] and not self.config["case_depart_secondaire"] == self.config["case_depart_principal"]:
            # Le robot secondaire a démarré sur une autre case que le robot principal : un deuxième emplacement est possible
            case_r2 = self.table.cases_depart[self.config["case_depart_secondaire"]-1]
            
            self.info_versions.append({   
                "point_entree_recherche_chemin": case_r2["centre"] + self.decalage_recherche_chemin,
                "point_entree": case_r2["centre"] + decalages_reglettes[1] + Point(-self.largeur_recul_piles*case_r2["nb_depots"],0),
                "id_case": self.config["case_depart_secondaire"]
            })
            
            return [0,1]
            
        else:
            return [0]
            
    def _execute(self, version):
        
        # Activation de la symétrie
        self.robot.effectuer_symetrie = True
        
        # Point d'entrée du script par recherche de chemin
        point_proche_case = self.info_versions[version]["point_entree_recherche_chemin"]
        self.robot.set_vitesse_translation("entre_scripts")
        self.robot.set_vitesse_rotation("entre_scripts")
        self.robot.recherche_de_chemin(point_proche_case, recharger_table=False)
        
        # On doit poser les verres contre le bord (x extremal) de la table au début, et revenir vers le centre si on est déjà passé
        orientation_vers_depot = 0
        
        # Déplacement au centre de la case, qui n'a normalement pas d'assiette
        point_depot = self.info_versions[version]["point_entree"]
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne = point_depot)

        self.robot.set_vitesse_translation("depot_verre")
        self.robot.set_vitesse_rotation("depot_verre")
        self.robot.va_au_point(point_depot)

        def deposer_avant(combo, sens_arriere):
            if self.robotVrai.deposer_verre_avant or combo:
                if combo:
                    #on se met du côté arrière!
                    self.robot.tourner(orientation_vers_depot - math.pi/6)

                    #attention, on va taper le bord de la table !
                    self.robot.avancer(self.distance_entree_depot, retenter_si_blocage=False, sans_lever_exception=True)
                    if sens_arriere:
                        self.robot.deposer_pile_combo(avant=True)
                    else:
                        self.robot.deposer_pile(avant=True)

                else:
                    #on dépose l'ascenseur avant d'un coté
                    self.robot.tourner(orientation_vers_depot + math.pi/6)

                    #attention, on va taper le bord de la table !
                    self.robot.avancer(self.distance_entree_depot, retenter_si_blocage=False, sans_lever_exception=True)

                    self.robot.deposer_pile(avant=True)
                self.robot.avancer(-self.distance_entree_depot)
        
        def deposer_arriere(combo, sens_arriere):
            if self.robotVrai.deposer_verre_arriere or combo:
                #on dépose l'ascenseur arrière de l'autre coté
                self.robot.tourner(math.pi + orientation_vers_depot - math.pi/6)

                #attention, on va taper le bord de la table !
                self.robot.avancer(-self.distance_entree_depot, retenter_si_blocage=False, sans_lever_exception=True)

                if not combo or sens_arriere:
                    self.robot.deposer_pile(avant=False)
                else:
                    self.robot.deposer_pile_combo(avant=False)
                self.robot.avancer(self.distance_entree_depot)
        
        #on retient un passage de plus dans cette case
        self.table.cases_depart[self.info_versions[version]["id_case"]-1]["nb_depots"] += 1
        
        #tenir compte de l'orientation d'arrivée pour commencer à l'avant ou à l'arrière
        position_verres = point_depot + Point(150*math.cos(orientation_vers_depot),150*math.sin(orientation_vers_depot))

        sens_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne=position_verres)
        combo = False
        if self.robot.nb_verres_avant == 1 and self.robot.nb_verres_arriere >= 1 and self.robot.nb_verres_arriere <= 3:
            combo = True
            sens_arriere = False
        elif self.robot.nb_verres_arriere == 1 and self.robot.nb_verres_avant >= 1 and self.robot.nb_verres_avant <= 3:
            combo = True
            sens_arriere = True

        if combo:
            self.log.debug("C-C-C-C-COMBOOO! Points bonus: "+str(4*max(self.robot.nb_verres_arriere, self.robot.nb_verres_avant)))

        if sens_arriere:
            deposer_arriere(combo, True)
            deposer_avant(combo, True)
        else:
            deposer_avant(combo, False)
            deposer_arriere(combo, False)
            
        #on se dégage
        self.robot.marche_arriere = self.robot.marche_arriere_est_plus_rapide(point_consigne=point_proche_case)
        self.robot.va_au_point(point_proche_case)
        
    def _termine(self):
        pass
            
    def point_entree(self, id_version):
        return self.info_versions[id_version]["point_entree"]

    def score(self):
        #on considère qu'on dépose une pile pour l'avant, une pile pour l'arrière
        return 4 * ( sum(range(1,self.robotVrai.nb_verres_avant+1)) + sum(range(1,self.robotVrai.nb_verres_arriere+1)) )

    def poids(self, t):
        # Ne pas oublier de déposer nos verres si on en a
        if not (self.robotVrai.places_disponibles(True) == self.config["nb_max_verre"] and self.robotVrai.places_disponibles(False) == self.config["nb_max_verre"]):
            #on calcule ici une valuation supplémentaire en fonction de l'avancée du match
            return 0.9347 * math.exp(0.053*t) #- 20
        else:
            return 0
            
#class ScriptRenverserVerres(Script):

    #def _constructeur(self):
	## Position des verres ennemis, mis à jour par la stratégie (0: pas de position)
        #self.cases_verres = [0,0]

    #def versions(self):
	##Autant de versions que de cases (le "list(set())" retire les doublons de la liste)
        #return [i for i in list(set(self.cases_verres)) if i!=0]

    #def _execute(self, version):
        #"""
        #On suppose connaître les emplacements de départ des autres robots (là où ils poseront leur verres).
        #"""
        #pass

    #def _termine(self):
        #pass
            
    #def point_entree(self, id_version):
        #entree = Point(900, 400*(id_version-0.5))
        #if self.config["rouge"]:
            #entree.x = -entree.x
        #return entree

    #def score(self):
        ## estimation
        #return 10

    #def poids(self):
        ## on le fera vers la fin
        #return 0.1*(time() - self.timer.get_date_debut())
