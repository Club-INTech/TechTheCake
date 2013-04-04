import math
from time import time,sleep
from mutex import Mutex
from outils_maths.point import Point
import hooks as hooks_module

#interface pour les méthodes publiques
from robotChrono import RobotInterface

class Robot(RobotInterface):
    """
    classe implémentant le robot.
    """
    def __init__(self,capteurs,actionneurs,deplacements,rechercheChemin,table,config,log):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.capteurs = capteurs
        self.actionneurs = actionneurs
        self.deplacements = deplacements
        self.rechercheChemin = rechercheChemin
        self.table = table
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
        
        #le nombre de verres dans l'ascenseur avant ou arrière
        self._nb_verres_avant = 0
        self._nb_verres_arriere = 0
        
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
            "nb_verres_avant":self.set_nb_verres_avant,
            "nb_verres_arriere":self.set_nb_verres_arriere
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
            "nb_verres_avant",
            "nb_verres_arriere"
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
        
    def set_nb_verres_avant(self, value):
        with self.mutex:
            self.__dict__["_nb_verres_avant"] = value
        
    def set_nb_verres_arriere(self, value):
        with self.mutex:
            self.__dict__["_nb_verres_arriere"] = value
     
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
        angle = round(math.atan2(delta_y,delta_x),4)
        
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

        while not self._acquittement(sans_lever_exception = sans_lever_exception):
            #vérification des hooks
            infosRobot = {"robotX": self.x, "robotY": self.y, "robotOrientation": self.orientation}
            for hook in hooks:
                hook.evaluate(**infosRobot)
                
            #mise à jour des consignes en translation et rotation
            if self.config["correction_trajectoire"]:
                self._mise_a_jour_consignes()
            #self._mise_a_jour_consignes()#@
            
            sleep(self.sleep_milieu_boucle_acquittement)
    
    def _mise_a_jour_consignes(self, arc_de_cercle=False):
        """
        Met à jour les consignes en translation et rotation (vise un point consigne)
        """
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(math.sqrt(delta_x**2 + delta_y**2),2)
        
        #gestion de la marche arrière du déplacement (peut aller à l'encontre de self.marche_arriere)
        angle = round(math.atan2(delta_y,delta_x),4)
        delta_angle = angle - self.maj_ancien_angle
        if delta_angle > math.pi: delta_angle -= 2*math.pi
        elif delta_angle <= -math.pi: delta_angle += 2*math.pi
        self.maj_ancien_angle = angle
        
        #print("###")#@
        #print(distance)#@
        #print(round(math.atan2(delta_y,delta_x),4))#@
        #if not self.config["correction_trajectoire"]:#@
            #return#@
            
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
        signe = -1 if self.marche_arriere else 1
        centre_detection = Point(self.x, self.y) + Point(signe * 200 * math.cos(self.orientation), signe * 200 * math.sin(self.orientation))
        for obstacle in self.table.obstacles():
            if obstacle.position.distance(centre_detection) < 200:
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
            
    def _arc_de_cercle(self,xM,yM,hooks=[]):
        """
        Effectue un arc de cercle à partir de la position courante vers le projetté de M sur le cercle passant par la position courante.
        Faites pas cette tête, c'est intuitif.
        Les hooks sont évalués, et une boucle d'acquittement générique est utilisée.
        """
        
        #distance, sur l'abscisse curviligne, à laquelle placer le point consigne au devant du robot
        pas = self.config["pas_arc_de_cercle"]
        
        #comme à toute consigne initiale de mouvement, le robot est débloqué
        self.blocage = False
        
        ######################
        ##si gateau en haut :
        ##sens de parcours
        if xM < self.x:
            pas *= -1
        ##centre du cercle
        xO = 0
        yO = 2000
        
        ####################
        #si gateau en bas :
        #sens de parcours
        #~ if xM > self.x:
            #~ pas *= -1
        #~ #centre du cercle
        #~ xO = 0
        #~ yO = 0
        
        #rayon du cercle
        r = float(math.sqrt((self.x-xO)**2+(self.y-yO)**2))
        #on ramène M sur le cercle : point B
        s = float(math.sqrt((xM-xO)**2+(yM-yO)**2))
        xB = xO + (r/s)*(xM-xO)
        yB = yO + (r/s)*(yM-yO)
        tB = math.atan2(yB-yO,xB-xO)
        
        #s'aligner sur la tangente au cercle :
        #calcul de l'angle de A (point de départ)
        tA = math.atan2(self.y-yO,self.x-xO)
        
        #vitesse de rotation pour atteindre la tangente
        self.set_vitesse_rotation(2)
        
        #ou exclusif entre le sens de parcours de l'abscisse curviligne (ie le sens de pas) et le mode marche arrière
        #afin de s'orienter perpendiculairement au rayon du cercle, dans la bonne direction
        if (pas < 0) != self.marche_arriere:
            angle = tA-math.pi/2
        else:
            angle = tA+math.pi/2
        self._tourner(angle)
        
        #initialisation de la marche
        self.maj_marche_arriere = self.marche_arriere
        self.maj_ancien_angle = angle
        
        #vitesses pour le parcours de l'arc de cercle
        #TODO : passer ca dans déplacements ?
        self.set_vitesse_translation(2)
        if "asservissement" in self.config["cartes_serie"]:
            #ATTENTION : cette vitesse est ajustée pour un rayon donné ! (celui utilisé pour enfoncer les bougies)
            self.set_vitesse_rotation(int(self.config["vitesse_rot_arc_cercle"]))
        else:
            self.set_vitesse_translation(2)
            
        
        while 1:
            #calcul de l'angle de A (point de départ)
            tA = math.atan2(self.y-yO,self.x-xO)
            
            #il reste au moins le pas à parcourir
            if (pas > 0 and r*tA+pas < r*tB) or (pas < 0 and r*tA+pas > r*tB):
                #nouveau point consigne : incrémenter l'abscisse curviligne de A du pas en mm
                #angle absolu pour C
                tC = tA + pas/r
                #coordonnées de C, prochain point consigne
                self.consigne_x = xO + r*math.cos(tC)
                self.consigne_y = yO + r*math.sin(tC)
                
                #vérification des hooks
                infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
                for hook in hooks:
                    hook.evaluate(**infosRobot)
                    
                #mise à jour des consignes en translation et rotation
                self._mise_a_jour_consignes(arc_de_cercle=True)
                
                #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
                acq = self._acquittement()
                if acq:
                    return acq
            else:
                #disque de tolérance atteint : on fixe la consigne au point d'arrivée
                
                #vitesse de rotation classique
                self.set_vitesse_rotation(20)
                
                #dernière mise à jour du point virtuel 
                self.consigne_x = xB
                self.consigne_y = yB
                
                #vérification des hooks
                infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
                for hook in hooks:
                    hook.evaluate(**infosRobot)
                    
                #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
                acq = self._acquittement()
                if acq:
                    return acq
            
            #on utilise ici une fréquence de mise à jour du point consigne
            sleep(1./self.config["freq_maj_arc_de_cercle"])
        
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
                    self.tourner(self.orientation + math.copysign(self.config["angle_degagement_robot"], -angle), [], nombre_tentatives=(nombre_tentatives-1), sans_lever_exception=sans_lever_exception)
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
    
    def recherche_de_chemin(self, arrivee, recharger_table=True, renvoie_juste_chemin=False):
        """
        Méthode pour atteindre un point de la carte après avoir effectué une recherche de chemin.
        """
        
        arrivee = arrivee.copy() #appliquer la symétrie ne doit pas modifier ce point !
        
        if recharger_table:
            self.rechercheChemin.retirer_obstacles_dynamiques()
            self.rechercheChemin.charge_obstacles()
            
        self.rechercheChemin.prepare_environnement_pour_visilibity()
        
        depart = Point(self.x,self.y)
        if self.effectuer_symetrie and self.config["couleur"] == "bleu":
            arrivee.x *= -1
        chemin = self.rechercheChemin.cherche_chemin_avec_visilibity(depart, arrivee)
        
        if renvoie_juste_chemin:
            return chemin
            
        self.suit_chemin(chemin, symetrie_effectuee=True)
    
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
                finally:
                    if not sans_lever_exception:
                        raise ExceptionMouvementImpossible(self)

        #détection d'un robot adverse
        except ExceptionCollision:
            self.stopper()
            if nombre_tentatives > 0:
                self.log.warning("attente avant nouvelle tentative... reste {0} tentative(s)".format(nombre_tentatives))
                sleep(0.5)
                self.va_au_point(point, hooks, trajectoire_courbe, nombre_tentatives-1, True)
            else:
                raise ExceptionMouvementImpossible(self)
            
            
    def arc_de_cercle(self, point_destination, hooks=[]):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet d'effectuer un arc de cercle à partir de la position courante vers le projetté de M sur le cercle passant par la position courante.
        Faites pas cette tête, c'est intuitif.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        self.log.debug("effectue un arc de cercle entre ("+str(self.x)+", "+str(self.y)+") et ("+str(point_destination)+")")
        
        #modification du disque de tolérance et marche automatique
        mem_marche_arriere =  self.marche_arriere
        self.marche_arriere = self.x > point_destination.x
        self.disque_tolerance_consigne = self.config["disque_tolerance_arc"]
         
        try:
            self._arc_de_cercle(point_destination.x, point_destination.y, hooks)
        
        #blocage durant le mouvement
        except ExceptionBlocage:
            raise ExceptionMouvementImpossible(self)
        
        #détection d'un robot adverse
        except ExceptionCollision:
            self.stopper()
            raise ExceptionMouvementImpossible(self)
        
        finally:
            self.disque_tolerance_consigne = self.config["disque_tolerance_maj"]
            self.marche_arriere = mem_marche_arriere
        
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
            self.x = -self.config["table_x"]/2. + self.config["largeur_robot"]/2.
        else:
            self.x = self.config["table_x"]/2. - self.config["largeur_robot"]/2.
        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(200, retenter_si_blocage = False, sans_lever_exception = True)

        #on se tourne pour le deuxième recalage
        self.tourner(math.pi/2, sans_lever_exception = True)
        
        #on recule lentement jusqu'à bloquer sur le bord
        self.marche_arriere = True
        self.avancer(-1000, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        #initialisation de la coordonnée y et de l'orientation
        #Le +100 en ordonnée correspond à la taille de l'estrade en bois (à mettre dans config?)
        self.y = self.config["largeur_robot"]/2.+100
        self.orientation = math.pi/2.
        
        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(150, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on prend l'orientation initiale pour le match (la symétrie est automatique pour les déplacements)
        self.tourner(math.pi, sans_lever_exception = True)

        #on recule lentement jusqu'à bloquer sur le bord
        self.set_vitesse_translation(1)
        self.set_vitesse_rotation(1)
        self.marche_arriere = True
        self.avancer(-1000, retenter_si_blocage = False, sans_lever_exception = True)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300, retenter_si_blocage = False, sans_lever_exception = True)
        
        if self.config["couleur"] == "bleu":
            self.orientation = 0.0-self.config["table_x"]
        else:
            self.orientation = math.pi+self.config["table_x"]

        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(200, retenter_si_blocage = False, sans_lever_exception = True)
        
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

    def traiter_bougie(self, enHaut):
        """
        teste la couleur puis enfonce si c'est la bonne couleur
        """
        self.actionneurs.enfoncer_bougie(enHaut)

    def initialiser_bras_bougie(self,enHaut) : 
        """
        Ouvre les bras qui soufflent les bougies
        """    
        self.actionneurs.initialiser_bras_bougie(enHaut)

    def rentrer_bras_bougie(self) : 
        """
        Rentre les bras qui ont soufflé les bougies
        """
        self.actionneurs.rentrer_bras_bougie()

    def ouvrir_cadeau(self):
        """
        Ouvre le bras qui pousse le cadeau
        """
        self.log.debug("ouverture du bras cadeaux")
        self.actionneurs.ouvrir_cadeau()
        
    def fermer_cadeau(self):
        """
        Ferme le bras qui a poussé le cadeau
        """
        self.log.debug("fermeture du bras cadeaux")
        self.actionneurs.fermer_cadeau()
 
    def recuperer_verre(self, avant):
        """
        Lance la procédure de récupération d'un verre
        """
        # Vérification de la capacité
        if self.places_disponibles(avant) == 0:
            if avant:
                self.log.critical("le robot ne peut pas porter plus de verres à l'avant")
            else:
                self.log.critical("le robot ne peut pas porter plus de verres à l'arrière")
            raise ExceptionMouvementImpossible(self)
        
        # Vérification de la présence du verre
        
        # Lancement des actionneurs
        
        # Mise à jour du total de verres portés
        super().recuperer_verre(avant)
            
        if avant:
            self.log.debug("saisit d'un verre à l'avant")
        else:
            self.log.debug("saisit d'un verre à l'arrière")
        self.log.debug("le robot a {0} verre(s) à l'avant, {1} à l'arrière".format(self.nb_verres_avant, self.nb_verres_arriere))
        
    def deposer_pile(self, avant):
        """
        Dépose l'ensemble des verres d'un ascenseur.
        """
        
        if avant:
            self.log.debug("Dépot de la pile de verres à l'avant.")
        else:
            self.log.debug("Dépot de la pile de verres à l'arrière.")
                
        # Lancement des actionneurs
        
        # Mise à jour du total de verres portés
        super().deposer_pile(avant)
        
    def gonflage_ballon(self):
        """
        Gonfle le ballon en fin de match
        """
        self.actionneurs.gonfler_ballon()
        
class RobotSimulation(Robot):
    def __init__(self, simulateur, capteurs, actionneurs, deplacements, rechercheChemin, table, config, log):
        super().__init__(capteurs, actionneurs, deplacements, rechercheChemin, table, config, log)
        self.simulateur = simulateur
        
    def tourner(self, angle_consigne, hooks=[], nombre_tentatives=2, sans_lever_exception=False):
        self._afficher_hooks(hooks)
        super().tourner(angle_consigne, hooks, sans_lever_exception=sans_lever_exception)
        
    def va_au_point(self, point, hooks=[], trajectoire_courbe=False, nombre_tentatives=2, retenter_si_blocage=True, symetrie_effectuee=False, sans_lever_exception=False):
        self._afficher_hooks(hooks)
        super().va_au_point(point, hooks, trajectoire_courbe=trajectoire_courbe, nombre_tentatives=nombre_tentatives, retenter_si_blocage=retenter_si_blocage, symetrie_effectuee=symetrie_effectuee, sans_lever_exception=sans_lever_exception)
        
    def arc_de_cercle(self, point, hooks=[]):
        self._afficher_hooks(hooks)
        super().arc_de_cercle(point, hooks)
        
    def _afficher_hooks(self, hooks):
        self.simulateur.clearEntity("hook")
        for hook in hooks:
            if isinstance(hook, hooks_module.HookPosition):
                self.simulateur.drawPoint(hook.position_hook.x, hook.position_hook.y, "black", "hook")
                self.simulateur.drawCircle(hook.position_hook.x, hook.position_hook.y, hook.tolerance_mm, False, "black", "hook")
            
            elif isinstance(hook, hooks_module.HookAngleGateau):
                if hook._callbacks[0].arguments[0]:
                    #bougie du haut
                    rayon_centre = 350
                else:
                    rayon_centre = 450
                    
                pt_centre = Point(0 + rayon_centre*math.cos(hook.angle_hook), 2000 + rayon_centre*math.sin(hook.angle_hook))
                pt_ext    = Point(0 + 800*math.cos(hook.angle_hook), 2000 + 800*math.sin(hook.angle_hook))
                self.simulateur.drawLine(pt_centre.x, pt_centre.y, pt_ext.x, pt_ext.y, "black", "hook")
        
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
