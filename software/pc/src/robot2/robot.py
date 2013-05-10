import math
from time import time,sleep
from mutex import Mutex
from outils_maths.point import Point

class Robot:
    """
    classe implémentant le robot secondaire
    """
    def __init__(self,capteurs,actionneurs,deplacements,hookGenerator,config,log):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.capteurs = capteurs
        self.actionneurs = actionneurs
        self.deplacements = deplacements
        self.hookGenerator = hookGenerator
        self.config = config
        self.log = log
        
        ###############################################
        #attributs des coordonnées et états du robot.
        #sont mis à jour automatiquement par un thread dédié communiquant via la série.

        #self.x, self.y, self.orientation : coordonnées courantes
        # (leurs valeurs initiales n'importent pas : le lanceur attend que le thread de mise à jour soit lancé)
        self._x = 0
        self._y = 0
        self._orientation = 0
        
        #self.blocage : booléen True si le robot est considéré comme bloqué hors de la consigne
        self._blocage = False
        #self.enMouvement : booléen True si le robot est encore en mouvement
        self._enMouvement = True
        
        #les écritures et lectures sur ces attributs (sans _devant) passent par des mutex gérant les accès mémoire, et communiquent avec la série si nécessaire
        ###############################################
        
        
        #point consigne pour la méthode va_au_point()
        self._consigne_x = 0
        self._consigne_y = 0
        
        #orientation initiale du robot : self._consigne_orientation est utilisé pour le fonctionnement de self._avancer()
        if self.config["couleur"] == "bleu":
            self._consigne_orientation = 0
        else:
            self._consigne_orientation = math.pi
        
        #sauvegarde des vitesses courantes du robot
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #disque de tolérance pour la mise à jour du point consigne
        self.disque_tolerance_consigne = self.config["disque_tolerance_maj"]
        
        #mode marche arrière
        self._marche_arriere = False
        
        #gestion par défaut de la symétrie couleur
        self._effectuer_symetrie = True
        
        #le robot n'est pas prêt tant qu'il n'a pas recu ses coordonnées initiales par le thread de mise à jour
        self.pret = False
        
        #sleep pour la boucle d'acquittement : divisé en 2 pour le simulateur, car il ne peut pas tourner et avancer en même temps
        if "asservissement" in self.config["cartes_simulation"]:
            self.sleep_milieu_boucle_acquittement = self.config["sleep_acquit_simu"]/2.
            self.sleep_fin_boucle_acquittement = self.config["sleep_acquit_simu"]/2.
        else:
            self.sleep_milieu_boucle_acquittement = self.config["sleep_acquit_serie"]
            self.sleep_fin_boucle_acquittement = 0.
        
        
    #####################################################################################
    ### ACCESSEURS SUR LES ATTRIBUTS DU ROBOT , MÉTHODES DE MISES À JOUR AUTOMATIQUES ###
    #####################################################################################
    
    def __setattr__(self, attribut, value):
        setters = {
            "x":self.set_x,
            "y":self.set_y,
            "consigne_x":self.set_consigne_x,
            "consigne_y":self.set_consigne_y,
            "orientation":self.set_orientation,
            "blocage":self.set_blocage,
            "enMouvement":self.set_enMouvement,
            "marche_arriere":self.set_marche_arriere,
            "effectuer_symetrie":self.set_effectuer_symetrie,
        }
        if attribut in setters:
            setters[attribut](value)
        else:
            self.__dict__[attribut] = value
            
    def __getattr__(self, attribut):
        getters = [
            "x",
            "y",
            "consigne_x",
            "consigne_y",
            "orientation",
            "blocage",
            "enMouvement",
            "marche_arriere",
            "effectuer_symetrie",
        ]
        if attribut in getters:
            with self.mutex:
                return self.__dict__["_"+attribut]
        
    def set_x(self, value):
        self.deplacements.set_x(value)
        
    def set_y(self, value):
        self.deplacements.set_y(value)
        
    def set_consigne_x(self, value):
        with self.mutex:
            self.__dict__["_consigne_x"] = value
            
    def set_consigne_y(self, value):
        with self.mutex:
            self.__dict__["_consigne_y"] = value
            
    def set_marche_arriere(self, value):
        with self.mutex:
            self.__dict__["_marche_arriere"] = value
            
    def set_effectuer_symetrie(self, value):
        with self.mutex:
            self.__dict__["_effectuer_symetrie"] = value
     
    def set_orientation(self, value):
        #l'attribut self._consigne_orientation doit etre mis à jour à chaque changement d'orientation pour le fonctionnement de self._avancer()
        self._consigne_orientation = value
        self.deplacements.set_orientation(value)
        
    def set_enMouvement(self, value):
        with self.mutex:
            self.__dict__["_enMouvement"] = value
            
    def set_blocage(self, value):
        with self.mutex:
            self.__dict__["_blocage"] = value
            
    def update_x_y_orientation(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de mise à jour des coordonnées du robot
        """
        [x,y,orientation_milliRadians] = self.deplacements.get_infos_x_y_orientation()
        with self.mutex:
            self.__dict__["_x"] = x
            self.__dict__["_y"] = y
            self.__dict__["_orientation"] = orientation_milliRadians/1000.
            
            
    #####################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE BASE , AVEC GESTION DES ACQUITTEMENTS ET CAPTEURS ###
    #####################################################################################
    
        
    def _avancer(self, distance, hooks=[]):
        """
        Cette méthode permet d'effectuer une translation en visant un point consigne devant le robot,
        au lieu d'avancer "en aveugle" : l'orientation est corrigée en cas de déviation
        Les hooks sont transmis à la méthode va_au_point()
        """
        
        #récupération de la dernière consigne d'orientation, et placement d'un point consigne au devant du robot
        consigne_x = self.x + distance*math.cos(self._consigne_orientation)
        consigne_y = self.y + distance*math.sin(self._consigne_orientation)

        return self._va_au_point(consigne_x,consigne_y,hooks=hooks,trajectoire_courbe=False)
        
        
    def _tourner(self, angle, hooks=[], sans_lever_exception = False):
        """
        Méthode de rotation en place.
        Les hooks sont évalués, et une boucle d'acquittement générique est utilisée.
        """
        
        #comme à toute consigne initiale de mouvement, le robot est débloqué
        self.blocage = False
        
        #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
        self._consigne_orientation = angle
        self.deplacements.tourner(angle)
        
        #pas de détection de collision dans les rotations
        while not self._acquittement(detection_collision=False, sans_lever_exception=sans_lever_exception):
            #vérification des hooks
            infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
            for hook in hooks:
                hook.evaluate(**infosRobot)
                
            sleep(self.sleep_milieu_boucle_acquittement)

        
    def _va_au_point(self, x, y, hooks=[], trajectoire_courbe=False, sans_lever_exception = False):
        """
        Méthode pour parcourir un segment : le robot se rend en (x,y) en corrigeant dynamiquement ses consignes en rotation et translation.
        Si le paramètre trajectoire_courbe=False, le robot évite d'effectuer un virage, et donc tourne sur lui meme avant la translation.
        Les hooks sont évalués, et une boucle d'acquittement générique est utilisée.
        """
        #comme à toute consigne initiale de mouvement, le robot est débloqué
        self.blocage = False
        
        #mise en place d'un point consigne, à atteindre (en attribut pour persister dans _mise_a_jour_consignes() )
        self.consigne_x = x
        self.consigne_y = y
        
        #au moins un déplacement, avant la boucle (équivalent à do...while)
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(math.sqrt(delta_x**2 + delta_y**2),2)
        angle = round(math.atan2(delta_y,delta_x),6)
        #initialisation de la marche dans mise_a_jour_consignes
        self.maj_marche_arriere = self.marche_arriere
        self.maj_ancien_angle = angle
                    
        #mode marche_arriere
        if self.marche_arriere:
            distance *= -1
            angle += math.pi 
            
        if not trajectoire_courbe:
            #sans virage : la première rotation est blocante
            self._tourner(angle)
            self._detecter_collisions() #on n'avance pas si un obstacle est devant
            self.deplacements.avancer(distance)

        else:
            #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            self._detecter_collisions() #on n'avance pas si un obstacle est devant
            self.deplacements.avancer(distance)

        #pas de détection de collision dans les rotations
        while not self._acquittement(sans_lever_exception = sans_lever_exception):
            #vérification des hooks
            infosRobot = {"robotX": self.x, "robotY": self.y, "robotOrientation": self.orientation}
            for hook in hooks:
                hook.evaluate(**infosRobot)
                
            #mise à jour des consignes en translation et rotation
            if self.config["correction_trajectoire"]:
                self._mise_a_jour_consignes()
            
            sleep(self.sleep_milieu_boucle_acquittement)

    def _mise_a_jour_consignes(self, arc_de_cercle=False):
        """
        Met à jour les consignes en translation et rotation (vise un point consigne)
        """
            
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(math.sqrt(delta_x**2 + delta_y**2),2)
        
        #gestion de la marche arrière du déplacement (peut aller à l'encontre de self.marche_arriere)
        angle = round(math.atan2(delta_y,delta_x),6)
        delta_angle = angle - self.maj_ancien_angle
        if delta_angle > math.pi: delta_angle -= 2*math.pi
        elif delta_angle <= -math.pi: delta_angle += 2*math.pi
        self.maj_ancien_angle = angle
        
        if not arc_de_cercle:
            #inversement de la marche si la destination n'est plus devant
            if abs(delta_angle) > math.pi/2: self.maj_marche_arriere = not self.maj_marche_arriere
            
        #mise à jour des consignes en translation et rotation en dehors d'un disque de tolérance
        if distance > self.disque_tolerance_consigne:
            
            #déplacement selon la marche
            if self.maj_marche_arriere:
                distance *= -1
                angle += math.pi
                  
            #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            #ce sleep est nécessaire au simulateur : les sleeps séparant rotation->translation et translation->rotation doivent etre les memes...
            sleep(self.sleep_fin_boucle_acquittement)
            self.deplacements.avancer(distance)
    
    def _detecter_collisions(self):
        if self.capteurs.adverse_devant(self.x, self.y, self.orientation):
            self.log.warning("ennemi détecté")
            raise ExceptionCollision
    
    def _acquittement(self, detection_collision=True, sans_lever_exception=False):
        """
        Boucle d'acquittement générique. Retourne des valeurs spécifiques en cas d'arrêt anormal (blocage, capteur)
        """
        #récupérations des informations d'acquittement
        #utilisées plusieurs fois : la notation **args permet aux méthodes appelées de n'utiliser que les paramètres dont elles ont besoin.
        infos = self.deplacements.get_infos_stoppage_enMouvement()
        #print(infos)#@
        
        #robot bloqué ?
        #self.deplacements.gestion_blocage() n'indique qu'un NOUVEAU blocage : garder le ou logique avant l'ancienne valeur (attention aux threads !)
        if self.blocage or self.deplacements.gestion_blocage(**infos):
            self.blocage = True
            raise ExceptionBlocage(self)
            
        #ennemi détecté devant le robot ?
        if detection_collision:
            self._detecter_collisions()

        #robot arrivé ?
        if not self.deplacements.update_enMouvement(**infos):
            return True
            
        #robot encore en mouvement
        return False
        
    #######################################################################################################################
    ### MÉTHODES PUBLIQUES DE DÉPLACEMENTS DE HAUT NIVEAU (TROUVÉES DANS LES SCRIPTS), AVEC RELANCES EN CAS DE PROBLÈME ###
    #######################################################################################################################
    
    def stopper(self):
        """
        Stoppe le robot en l'asservissant sur place
        """
        self.log.debug("stoppage du robot")
        self.blocage = True
        self.deplacements.stopper()

    def avancer(self, distance, hooks=[], nombre_tentatives=2, retenter_si_blocage=True, sans_lever_exception=False):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet d'effectuer une translation en visant un point consigne devant le robot,
        au lieu d'avancer "en aveugle" : l'orientation est corrigée en cas de déviation.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        self.log.debug("avancer de "+str(distance))
        
        #sauvegarde des paramètres de trajectoire
        mem_marche_arriere, mem_effectuer_symetrie = self.marche_arriere, self.effectuer_symetrie
        
        self.marche_arriere = (distance < 0)
        self.effectuer_symetrie = False
        
        x = self.x + distance * math.cos(self._consigne_orientation)
        y = self.y + distance * math.sin(self._consigne_orientation)
        
        try:
            self.va_au_point(Point(x, y), hooks, nombre_tentatives=nombre_tentatives, retenter_si_blocage=retenter_si_blocage, sans_lever_exception=sans_lever_exception)
        except ExceptionMouvementImpossible:
            raise ExceptionMouvementImpossible(self)
        finally:
            #rétablissement des paramètres de trajectoire
            self.marche_arriere, self.effectuer_symetrie = mem_marche_arriere, mem_effectuer_symetrie
        
    def tourner(self, angle, hooks=[], nombre_tentatives=2, sans_lever_exception=False):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle effectue une rotation en place. La symétrie est prise en compte.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        if self.effectuer_symetrie:
            if self.config["couleur"] == "bleu":
                angle = math.pi - angle
            self.log.debug("tourner à "+str(angle)+" (symétrie appliquée)")
        else:
            self.log.debug("tourner à "+str(angle)+" (sans symétrie)")
                
        try:
            self._tourner(angle, hooks, sans_lever_exception = sans_lever_exception)
            
        #blocage durant la rotation
        except ExceptionBlocage:
            try:
                if nombre_tentatives > 0:
                    self.log.warning("Blocage en rotation ! On tourne dans l'autre sens... reste {0} tentative(s)".format(nombre_tentatives))
                    self.tourner(self.orientation + math.copysign(self.config["angle_degagement_robot"], -angle), [], nombre_tentatives=nombre_tentatives-1, sans_lever_exception=sans_lever_exception)
            finally:
                if not sans_lever_exception:
                    raise ExceptionMouvementImpossible(self)
                
        #détection d'un robot adverse
        except ExceptionCollision:
            self.stopper()
            raise ExceptionMouvementImpossible(self)
            
    def suit_chemin(self, chemin, hooks=[], marche_arriere_auto=True, symetrie_effectuee=False):
        """
        Cette méthode parcourt un chemin déjà calculé. Elle appelle va_au_point() sur chaque point de la liste chemin.
        """
        for position in chemin:
            if marche_arriere_auto:
                self.marche_arriere = self.marche_arriere_est_plus_rapide(position)
            self.va_au_point(position, hooks, symetrie_effectuee=symetrie_effectuee)
    
    def va_au_point(self, point, hooks=[], trajectoire_courbe=False, nombre_tentatives=2, retenter_si_blocage=True, symetrie_effectuee=False, sans_lever_exception=False):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet de parcourir un segment : le robot se rend en (x,y) en corrigeant dynamiquement ses consignes en rotation et translation.
        La symétrie est prise en compte.
        Si le paramètre trajectoire_courbe=False, le robot évite d'effectuer un virage, et donc tourne sur lui meme avant la translation.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        point = point.copy() #appliquer la symétrie ne doit pas modifier ce point !
        
        #application de la symétrie si demandée et si pas déjà faite
        if self.effectuer_symetrie and not symetrie_effectuee:
            if self.config["couleur"] == "bleu":
                point.x *= -1
            self.log.debug("va au point ({0}) (symétrie vérifiée pour le {1}), virage initial: {2}".format(point, self.config["couleur"], trajectoire_courbe))
        else:
            self.log.debug("va au point ({0}) (sans symétrie pour la couleur), virage initial: {1}".format(point, trajectoire_courbe))
                
        try:
            self._va_au_point(point.x, point.y, hooks=hooks, trajectoire_courbe=trajectoire_courbe, sans_lever_exception = sans_lever_exception)
        #blocage durant le mouvement
        except ExceptionBlocage:
                try:
                    self.stopper()
                    if retenter_si_blocage:
                        #TODO On tente de reculer. Mais l'exception est peut etre levée lors d'un virage...
                        if nombre_tentatives > 0:
                            self.log.warning("Blocage en déplacement ! On recule... reste {0} tentative(s)".format(nombre_tentatives))
                            if self.marche_arriere:
                                self.avancer(self.config["distance_degagement_robot"], nombre_tentatives=nombre_tentatives-1)
                            else:
                                self.avancer(-self.config["distance_degagement_robot"], nombre_tentatives=nombre_tentatives-1)
                except:
                    if not sans_lever_exception:
                        raise ExceptionMouvementImpossible(self)

        #détection d'un robot adverse
        except ExceptionCollision:
            self.stopper()
            if nombre_tentatives > 0:
                self.log.warning("attente avant nouvelle tentative... reste {0} tentative(s)".format(nombre_tentatives))
                sleep(1)
                self.va_au_point(point, hooks, trajectoire_courbe, nombre_tentatives-1, True)
            else:
                raise ExceptionMouvementImpossible(self)

    def recaler(self):
        """
        Recalage du robot sur les bords de la table, pour initialiser ses coordonnées.
        """
        
        self.log.debug("début du recalage")
        
        #on recule lentement jusqu'à bloquer sur le bord
        self.set_vitesse_translation(1)
        self.set_vitesse_rotation(1)
        self.marche_arriere = True
        self.avancer(-1000, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        #initialisation de la coordonnée x et de l'orientation
        if self.config["couleur"] == "bleu":
            self.x = -self.config["table_x"]/2. + self.config["r2_epaisseur_arriere"]/2.
            self.orientation = 0.0+self.config["r2_epsilon_angle"]
        else:
            self.x = self.config["table_x"]/2. - self.config["r2_epaisseur_arriere"]/2.
            self.orientation = math.pi+self.config["r2_epsilon_angle"]

        # Ce sleep est nécessaire. En effet, la mise à jour de self.x et de self.y n'est pas immédiate (on passe par la carte d'asserv et tout) et sans sleep la mise à jour se fait pendant l'appel d'avancer, ce qui la fait bugger. Plus exactement, avancer transforme une distance en un point en se basant sur l'ancienne position (la mise à jour n'étant pas encore effectuée), puis va_au_point retransforme ce point en distance, mais cette fois en basant sur la position du robot mise à jour, ce qui fait que la distance obtenue au final n'est pas celle donnée au départ. Normalement, ce problème n'arrive que quand on modifie robot.x et robot.y, c'est-à-dire dans la méthode recaler, là où un sleep n'est pas trop ennuyeux
        sleep(1)

        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(500, retenter_si_blocage = False, sans_lever_exception = True)

        #on se tourne pour le deuxième recalage
        #on se dirige vers le côté le plus proche
        if self.config["case_depart_secondaire"] <= 3:
            cote_bas = True
            self.tourner(math.pi/2, sans_lever_exception = True)
        else:
            cote_bas = False
            self.tourner(-math.pi/2, sans_lever_exception = True)
        
        #on recule lentement jusqu'à bloquer sur le bord
        self.marche_arriere = True
        self.set_vitesse_translation(1)
        self.avancer(-abs(400*(self.config["case_depart_secondaire"]-0.5)), retenter_si_blocage = False, sans_lever_exception = True)

        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        #initialisation de la coordonnée y et de l'orientation
        if cote_bas:
            self.y = self.config["r2_epaisseur_arriere"]/2.
        else:
            self.y = self.config["table_y"]-self.config["r2_epaisseur_arriere"]/2.
        
        #nécessaire, cf plus haut
        sleep(1)

        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(abs(self.y-400*(self.config["case_depart_secondaire"]-0.5)), retenter_si_blocage = False, sans_lever_exception = True)
        
        #on prend l'orientation initiale pour le match (la symétrie est automatique pour les déplacements)
        self.tourner(math.pi, sans_lever_exception = True)

        #on recule lentement jusqu'à bloquer sur le bord
        self.set_vitesse_rotation(1)
        self.marche_arriere = True
        self.avancer(-700, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        if self.config["couleur"] == "bleu":
            self.orientation = 0.0+self.config["r2_epsilon_angle"]
            self.x = -self.config["table_x"]/2. + self.config["r2_epaisseur_arriere"]/2.
        else:
            self.orientation = math.pi+self.config["r2_epsilon_angle"]
            self.x = self.config["table_x"]/2. - self.config["r2_epaisseur_arriere"]/2.

        # nécessaire, cf plus haut
        sleep(1)

        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()

        #vitesse initiales pour le match
        self.set_vitesse_translation(2)
        self.set_vitesse_rotation(2)
       
        self.log.debug("recalage terminé")
        
    def set_vitesse_translation(self, valeur):
        """
        modifie la vitesse de translation du robot et adapte les constantes d'asservissement
        """
        self.deplacements.set_vitesse_translation(valeur)
        self.vitesse_translation = int(valeur)
        
    def set_vitesse_rotation(self, valeur):
        """
        modifie la vitesse de rotation du robot et adapte les constantes d'asservissement
        """
        self.deplacements.set_vitesse_rotation(valeur)
        self.vitesse_rotation = int(valeur)

    def actionneur_balai(self, position):
        """
        Commande l'actionneur balai
        """
        self.log.debug("Actionneur balai: "+position)
        self.actionneurs.actionneur_balai(position)
        
class RobotSimulation(Robot):
    def __init__(self, simulateur, capteurs, actionneurs, deplacements, hookGenerator, config, log):
        super().__init__(capteurs, actionneurs, deplacements, hookGenerator, config, log)
        self.simulateur = simulateur
        
    def tourner(self, angle_consigne, hooks=[], nombre_tentatives=2, sans_lever_exception=False):
        super().tourner(angle_consigne, hooks, sans_lever_exception=sans_lever_exception)
        
    def va_au_point(self, point, hooks=[], trajectoire_courbe=False, nombre_tentatives=2, retenter_si_blocage=True, symetrie_effectuee=False, sans_lever_exception=False):
        super().va_au_point(point, hooks, trajectoire_courbe=trajectoire_courbe, nombre_tentatives=nombre_tentatives, retenter_si_blocage=retenter_si_blocage, symetrie_effectuee=symetrie_effectuee, sans_lever_exception=sans_lever_exception)
        
class ExceptionBlocage(Exception):
    """
    Exception levée lorsque le robot est physiquement bloqué par un obstacle
    """
    def __init__(self, robot):
        robot._consigne_orientation = robot.orientation
    
class ExceptionCollision(Exception):
    """
    Exception levée lorsque le robot rencontre devant lui un obstacle avec ses capteurs
    """
    pass
        
class ExceptionMouvementImpossible(Exception):
    """
    Exception levée lorsque le robot ne peut pas accomplir le mouvement
    """
    def __init__(self, robot):
        robot._consigne_orientation = robot.orientation