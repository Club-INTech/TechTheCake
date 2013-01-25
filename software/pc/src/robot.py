from math import pi,sqrt,atan2,atan,cos,sin
from time import time,sleep
from mutex import Mutex

class Robot:
    """
    classe implémentant le robot.
    """
    def __init__(self,capteurs,actionneurs,deplacements,config,log,table):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.deplacements = deplacements
        self.actionneurs = actionneurs
        self.capteurs = capteurs
        self.config = config
        self.log = log
        self.table = table
        
        
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
            self._consigne_orientation = pi
        
        #sauvegarde des vitesses courantes du robot
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #mode marche arrière
        self.marche_arriere = False
        
        #le robot n'est pas prêt tant qu'il n'a pas recu ses coordonnées initiales par le thread de mise à jour
        self.pret = False
        
        #le nombre de verres dans l'ascenseur avant ou arrière
        self.nb_verres_avant = 0
        self.nb_verres_arriere = 0
        
        #sleep pour la boucle d'acquittement : divisé en 2 pour le simulateur, car il ne peut pas tourner et avancer en même temps
        if self.config["mode_simulateur"]:
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
            "enMouvement":self.set_enMouvement
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
            "enMouvement"
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
        consigne_x = self.x + distance*cos(self._consigne_orientation)
        consigne_y = self.y + distance*sin(self._consigne_orientation)
        
        return self._va_au_point(consigne_x,consigne_y,hooks,False)
        
        
    def _tourner(self, angle, hooks=[]):
        """
        Méthode de rotation en place.
        Les hooks sont évalués, et une boucle d'acquittement générique est utilisée.
        """
        
        #comme à toute consigne initiale de mouvement, le robot est débloqué
        self.blocage = False
        #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
        self._consigne_orientation = angle
        self.deplacements.tourner(angle)
        while 1:
            #vérification des hooks
            infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
            for hook in hooks:
                hook.evaluate(**infosRobot)
                
            #acquittement du déplacement : sort de la boucle (avec un return) si robot arrivé ou bloqué
            acq = self._acquittement()
            if acq:
                return acq
            
            sleep(self.sleep_milieu_boucle_acquittement)
        
    def _va_au_point(self, x, y, hooks=[], virage_initial=False):
        """
        Méthode pour parcourir un segment : le robot se rend en (x,y) en corrigeant dynamiquement ses consignes en rotation et translation.
        Si le paramètre virage_initial=False, le robot évite d'effectuer un virage, et donc tourne sur lui meme avant la translation.
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
        distance = round(sqrt(delta_x**2 + delta_y**2),2)
        angle = round(atan2(delta_y,delta_x),4)
        #mode marche_arriere
        if self.marche_arriere:
            distance *= -1
            angle += pi 
        if not virage_initial:
            #sans virage : la première rotation est blocante
            self._tourner(angle)
            self.deplacements.avancer(distance)
        else:
            #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            self.deplacements.avancer(distance)
            
        while 1:
            #vérification des hooks
            infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
            for hook in hooks:
                hook.evaluate(**infosRobot)
                
            #mise à jour des consignes en translation et rotation
            if self.config["correction_trajectoire"]:
                self._mise_a_jour_consignes()
            
            #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
            acq = self._acquittement()
            if acq:
                return acq
            
            sleep(self.sleep_milieu_boucle_acquittement)
    
    def _mise_a_jour_consignes(self):
        """
        Met à jour les consignes en translation et rotation (vise un point consigne)
        """
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(sqrt(delta_x**2 + delta_y**2),2)
        #mise à jour des consignes en translation et rotation en dehors d'un disque de tolérance
        if distance > self.config["disque_tolerance"]:
            angle = round(atan2(delta_y,delta_x),4)
            #mode marche_arriere
            if self.marche_arriere:
                distance *= -1
                angle += pi 
                
            #l'attribut self._consigne_orientation doit etre mis à jour à chaque deplacements.tourner() pour le fonctionnement de self._avancer()
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            #ce sleep est nécessaire au simulateur : les sleeps séparant rotation->translation et translation->rotation doivent etre les memes...
            sleep(self.sleep_fin_boucle_acquittement)
            self.deplacements.avancer(distance)
            
    
    def _acquittement(self):
        """
        Boucle d'acquittement générique. Retourne des valeurs spécifiques en cas d'arrêt anormal (blocage, capteur)
        """
        #récupérations des informations d'acquittement
        #utilisées plusieurs fois : la notation **args permet aux méthodes appelées de n'utiliser que les paramètres dont elles ont besoin.
        infos = self.deplacements.get_infos_stoppage_enMouvement()
        
        #robot bloqué ?
        #self.deplacements.gestion_blocage() n'indique qu'un NOUVEAU blocage : garder le ou logique avant l'ancienne valeur (attention aux threads !)
        if self.blocage or self.deplacements.gestion_blocage(**infos):
            self.blocage = True
            #abandon car blocage
            return 2
        #robot arrivé ?
        if not self.deplacements.update_enMouvement(**infos):
            #robot arrivé
            return 1
            
            
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
        
        #TODO : utiliser le service de table pour le gateau ?
        #####################
        ##si gateau en haut :
        ##sens de parcours
        #if xM < self.x:
            #pas *= -1
        ##centre du cercle
        #xO = 0
        #yO = 2000
        
        #####################
        #si gateau en bas :
        #sens de parcours
        if xM > self.x:
            pas *= -1
        #centre du cercle
        xO = 0
        yO = 0
        
        #rayon du cercle
        r = float(sqrt((self.x-xO)**2+(self.y-yO)**2))
        #on ramène M sur le cercle : point B
        s = float(sqrt((xM-xO)**2+(yM-yO)**2))
        xB = xO + (r/s)*(xM-xO)
        yB = yO + (r/s)*(yM-yO)
        tB = atan2(yB-yO,xB-xO)
        
        #s'aligner sur la tangente au cercle :
        #calcul de l'angle de A (point de départ)
        tA = atan2(self.y-yO,self.x-xO)
        
        #vitesse de rotation pour atteindre la tangente
        self.set_vitesse_rotation(1)
        
        #ou exclusif entre le sens de parcours de l'abscisse curviligne (ie le sens de pas) et le mode marche arrière
        #afin de s'orienter perpendiculairement au rayon du cercle, dans la bonne direction
        if (pas < 0) != self.marche_arriere:
            self._tourner(tA-pi/2)
        else:
            self._tourner(tA+pi/2)
        
        #vitesses pour le parcours de l'arc de cercle
        #TODO : passer ca dans déplacements ?
        self.set_vitesse_translation(1)
        self.deplacements.serie.communiquer("asservissement",["crv",1.5,2.0,self.config["vitesse_rot_arc_cercle"]], 0)
        
        while 1:
            #calcul de l'angle de A (point de départ)
            tA = atan2(self.y-yO,self.x-xO)
            
            #il reste au moins le pas à parcourir
            if (pas > 0 and r*tA+pas < r*tB) or (pas < 0 and r*tA+pas > r*tB):
                #nouveau point consigne : incrémenter l'abscisse curviligne de A du pas en mm
                #angle absolu pour C
                tC = tA + pas/r
                #coordonnées de C, prochain point consigne
                self.consigne_x = xO + r*cos(tC)
                self.consigne_y = yO + r*sin(tC)
                
                #vérification des hooks
                infosRobot={"robotX" : self.x,"robotY" : self.y,"robotOrientation" : self.orientation}
                for hook in hooks:
                    hook.evaluate(**infosRobot)
                    
                #mise à jour des consignes en translation et rotation
                self._mise_a_jour_consignes()
                
                #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
                acq = self._acquittement()
                if acq:
                    return acq
            else:
                #disque de tolérance atteint : on fixe la consigne au point d'arrivée
                
                #vitesse de rotation classique
                self.set_vitesse_rotation(1)
                
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
        
    def avancer(self, distance, hooks=[]):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet d'effectuer une translation en visant un point consigne devant le robot,
        au lieu d'avancer "en aveugle" : l'orientation est corrigée en cas de déviation.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        self.log.debug("avancer de "+str(distance))
        
        retour = self._avancer(distance, hooks)
        if retour == 1:
            print("translation terminée !")
        elif retour == 2:
            self.stopper()
            print("translation arrêtée car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
        
    def tourner(self, angle, hooks=[]):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle effectue une rotation en place. La symétrie est prise en compte.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        self.log.debug("tourner à "+str(angle))
        
        #le mode marche arrière n'effectue pas de symétrie pour la couleur : on l'utilise justement pour ca. (actionneurs sur le côté)
        if not self.marche_arriere:
            if self.config["couleur"] == "bleu":
                #symétrie de la consigne d'orientation
                angle = pi - angle
                
        retour = self._tourner(angle, hooks)
        if retour == 1:
            print("rotation terminée !")
        elif retour == 2:
            self.stopper()
            print("rotation arrêtée car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
            
    def suit_chemin(self, chemin, hooks=[]):
        """
        Cette méthode parcourt un chemin déjà calculé. Elle appelle va_au_point() sur chaque point de la liste chemin.
        """
        for position in chemin:
            self.va_au_point(position.x, position.y, hooks)
            
    def va_au_point(self, x, y, hooks=[], virage_initial=False):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet de parcourir un segment : le robot se rend en (x,y) en corrigeant dynamiquement ses consignes en rotation et translation.
        La symétrie est prise en compte.
        Si le paramètre virage_initial=False, le robot évite d'effectuer un virage, et donc tourne sur lui meme avant la translation.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        self.log.debug("va au point ("+str(x)+", "+str(y)+"), virage inital : "+str(virage_initial))
        
        if self.config["couleur"] == "bleu":
            #symétrie du point consigne
            x *= -1
                
        retour = self._va_au_point(x, y, hooks, virage_initial)
        if retour == 1:
            print("point de destination atteint !")
        elif retour == 2:
            print("déplacement arrêté car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
            
    def arc_de_cercle(self,xM,yM,hooks=[]):
        """
        Cette méthode est une surcouche intelligente sur les déplacements.
        Elle permet d'effectuer un arc de cercle à partir de la position courante vers le projetté de M sur le cercle passant par la position courante.
        Faites pas cette tête, c'est intuitif.
        Les hooks sont executés, et différentes relances sont implémentées en cas de retour particulier.
        """
        
        self.log.debug("effectue un arc de cercle entre ("+str(self.x)+", "+str(self.y)+") et ("+str(xM)+", "+str(yM)+")")
        
        if self.config["couleur"] == "bleu":
            #symétrie du point consigne
            xM *= -1
                
        retour = self._arc_de_cercle(xM,yM,hooks)
        if retour == 1:
            print("point de destination atteint !")
        elif retour == 2:
            print("déplacement arrêté car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
        
    def recaler(self):
        """
        Recalage du robot sur les bords de la table, pour initialiser ses coordonnées.
        """
        
        self.log.debug("début du recalage")
        
        #on recule lentement jusqu'à bloquer sur le bord
        self.set_vitesse_translation(1)
        self.set_vitesse_rotation(1)
        self.marche_arriere = True
        self.avancer(-1000)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300)
        
        #initialisation de la coordonnée x et de l'orientation
        if self.config["couleur"] == "bleu":
            self.x = -self.config["table_x"]/2. + self.config["largeur_robot"]/2.
            self.orientation = 0.0
        else:
            self.x = self.config["table_x"]/2. - self.config["largeur_robot"]/2.
            self.orientation = pi
        
        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(100)
        
        #on se tourne pour le deuxième recalage
        self.tourner(pi/2)
        
        #on recule lentement jusqu'à bloquer sur le bord
        self.marche_arriere = True
        self.avancer(-1000)
        
        #on désactive l'asservissement en rotation pour se mettre parallèle au bord
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.avancer(-300)
        
        #initialisation de la coordonnée y et de l'orientation
        self.y = self.config["largeur_robot"]/2.
        self.orientation = pi/2.
        
        #on avance doucement, en réactivant l'asservissement en rotation
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.avancer(150)
        
        #on prend l'orientation initiale pour le match (la symétrie est automatique pour les déplacements)
        self.tourner(pi)
        
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

    def traiter_bougie(self):
        """
        teste la couleur puis enfonce si c'est la bonne couleur
        """
        if(self.capteurs.lire_couleur() == self.couleur):
            self.actionneurs.enfoncer_bougie()
            sleep(1)
            self.actionneurs.initialiser_bras_bougie()
        self.table.bougie_recupere(0) #ne pas oublier de mettre à jour les éléments de jeu dans le service de table! (ligne à fin de test)
    
    def ouvrir_cadeau(self):
        """
        Ouvre le bras qui pousse le cadeau
        """
        self.actionneurs.ouvrir_cadeau()
        self.table.cadeau_recupere(0) #ne pas oublier de mettre à jour les éléments de jeu dans le service de table! (ligne à fin de test)
        
    def fermer_cadeau(self):
        """
        Ferme le bras qui a poussé le cadeau
        """
        self.actionneurs.fermer_cadeau()
        
    def gonflage_ballon(self):
        """
        Gonfle le ballon en fin de match
        """
        self.actionneurs.gonfler_ballon()
        
