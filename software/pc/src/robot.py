from math import pi,sqrt,atan2,atan,cos,sin
from time import time,sleep
from mutex import Mutex

class Robot:
    def __init__(self,capteurs,deplacements,config,log):
        self.mutex = Mutex()
        
        #instances des dépendances
        self.deplacements = deplacements
        self.capteurs=capteurs
        self.config = config
        self.log = log
        
        """
        attributs des coordonnées du robot.
        sont mis à jour automatiquement par un thread dédié communiquant via la série.
        dans le code, on peut utiliser directement :
        self.x, self.y, self.orientation : coordonnées courantes
        self.blocage : booléen True si le robot est considéré comme bloqué hors de la consigne
        self.enMouvement : booléen True si le robot est encore en mouvement
        les écritures et lectures sur ces attributs passent par des mutex gérant les accès mémoire, et communiquent avec la série si nécessaire
        """
        
        #TODO variables à ajuster puis passer dans le service config
        if self.config["mode_simulateur"]:
            self.sleep_boucle_acquittement = 0.05
            self.frequence_maj_arc_de_cercle = 20
            self.pas = 100
            self.vitesse_rotation_arc_cercle = 10
            
            
        else:
            self.sleep_boucle_acquittement = 0.1
            self.frequence_maj_arc_de_cercle = 20
            self.pas = 100
            self.vitesse_rotation_arc_cercle = 10
        
        #couleur du robot
        self.couleur = self.config["couleur"]
            
        self._x = 0
        self._y = 0
        self._orientation = 0
        
        self._consigne_x = 0
        self._consigne_y = 0
        
        if self.couleur == "bleu":
            self._consigne_orientation = 0
        else:
            self._consigne_orientation = pi
        
        self._blocage = False
        self._enMouvement = True
        
        #sauvegarde des vitesses courantes du robot
        self.vitesse_translation = 2
        self.vitesse_rotation = 2
        
        #mode marche arrière
        self.marche_arriere = False
        
        #durée de jeu TODO : à muter dans Table ?
        self.debut_jeu = time()
        
        #le robot n'est pas prêt tant qu'il n'a pas recu ses coordonnées initiales par le thread de mise à jour
        self.pret = False
        
        
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
    
    def stopper(self):
        self.log.debug("stoppage du robot")
        self.blocage = True
        self.deplacements.stopper()
        
    def avancer(self, distance, hooks=[]):
        self.log.debug("avancer de "+str(distance))
        
        consigne_x = self.x + distance*cos(self._consigne_orientation)
        consigne_y = self.y + distance*sin(self._consigne_orientation)
        
        return self.va_au_point(consigne_x,consigne_y,hooks,False)
        
        
    def tourner(self, angle, hooks=[]):
        self.log.debug("tourner à "+str(angle))
        self.blocage = False
        self._consigne_orientation = angle
        self.deplacements.tourner(angle)
        while 1:
            #vérification des hooks
            for hook in hooks:
                hook.evaluate()
                
            #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
            acq = self._acquittement()
            if acq:
                return acq
            
            if self.config["mode_simulateur"]:
                #sleep nécessaire pour le simulateur
                sleep(self.sleep_boucle_acquittement/2.)
            else:
                sleep(self.sleep_boucle_acquittement)
        
    def va_au_point(self, x, y, hooks=[], virage_initial=False):
        
        self.set_vitesse_rotation(1)
        self.set_vitesse_translation(1)
                
        self.log.debug("va au point ("+str(x)+", "+str(y)+"), virage inital : "+str(virage_initial))
        
        self.blocage = False
        self.consigne_x = x
        self.consigne_y = y
        
        #au moins un déplacement
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(sqrt(delta_x**2 + delta_y**2),2)
        angle = round(atan2(delta_y,delta_x),4)
        if self.marche_arriere:
            distance *= -1
            angle += pi 
        if not virage_initial:
            #sans virage : la première rotation est blocante
            self.tourner(angle)
            self.log.debug("rotation initiale terminée, va maintenant au point ("+str(x)+", "+str(y)+")")
            self.deplacements.avancer(distance)
        else:
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            print("1ère rotation: cour="+str(self.orientation)+" cons="+str(self._consigne_orientation))
            self.deplacements.avancer(distance)
            
        while 1:
            #vérification des hooks
            for hook in hooks:
                hook.evaluate()
                
            #mise à jour des consignes en translation et rotation
            if self.config["correction_trajectoire"]:
                self._mise_a_jour_consignes()
            
            #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
            acq = self._acquittement()
            if acq:
                return acq
            
            if self.config["mode_simulateur"]:
                #sleep nécessaire pour le simulateur
                sleep(self.sleep_boucle_acquittement/2.)
            else:
                sleep(self.sleep_boucle_acquittement)
    
    # Met à jour les consignes en translation et rotation (vise un point)
    def _mise_a_jour_consignes(self):
        delta_x = self.consigne_x-self.x
        delta_y = self.consigne_y-self.y
        distance = round(sqrt(delta_x**2 + delta_y**2),2)
        if distance > 30:
            ############################
            angle = round(atan2(delta_y,delta_x),4)
            #self.log.debug("distance calculée : "+str(distance))
            #self.log.debug("angle calculé : "+str(angle))
            ############################
            #if delta_x == 0:
                #if delta_y > 0:
                    #angle = pi/2
                #else:
                    #angle = -pi/2
            #else:
                #angle = atan(delta_y/delta_x)
            #if delta_x < 0:
                #if distance < 150:
                    #distance = -distance
                #elif delta_y > 0:
                    #angle += pi
                #else:
                    #angle -= pi
            ############################
            if self.marche_arriere:
                distance *= -1
                angle += pi 
                
            self._consigne_orientation = angle
            self.deplacements.tourner(angle)
            if self.config["mode_simulateur"]:
                #sleep nécessaire pour le simulateur
                sleep(self.sleep_boucle_acquittement/2.)
            self.deplacements.avancer(distance)
        else:
            #self.log.debug("robot dans le disque de tolérance, pas de mise à jour des consignes.")
            pass
            
    # S'utilise dans la boucle d'acquittement. Remonte des exceptions en cas d'arrêt anormal (blocage, capteur etc...)
    def _acquittement(self):
        #récupérations des informations d'acquittement
        infos = self.deplacements.get_infos_stoppage_enMouvement()
        
        #print("infos :")
        #for i in infos:
            #print(i+" : "+str(infos[i]))
            
        #robot bloqué ?
        if self.blocage or self.deplacements.gestion_blocage(**infos):
            self.blocage = True
            #abandon car blocage
            return 2
        #robot arrivé ?
        if not self.deplacements.update_enMouvement(**infos):
            #robot arrivé
            return 1
            
            
    def arc_de_cercle(self,xM,yM,hooks=[]):
        #effectue un arc de cercle à partir de la position courante vers le projetté de M sur le cercle passant par la position courante
        
        pas = self.pas
        
        self.log.debug("effectue un arc de cercle entre ("+str(self.x)+", "+str(self.y)+") et ("+str(xM)+", "+str(yM)+")")
        self.blocage = False
        
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
        
        #TODO : visualisation à enlever
        if self.config["mode_simulateur"]:
            self.deplacements.simulateur.drawPoint(xB,yB,"red",True)
        
        #s'aligner sur la tangente au cercle :
        #calcul de l'angle de A (point de départ)
        tA = atan2(self.y-yO,self.x-xO)
        
        self.set_vitesse_rotation(1)
        if (pas < 0) != self.marche_arriere:
            self.tourner(tA-pi/2)
        else:
            self.tourner(tA+pi/2)
        
        #vitesses pour l'arc de cercle
        self.set_vitesse_translation(1)
        self.deplacements.serie.communiquer("asservissement",["crv",1.5,2.0,self.vitesse_rotation_arc_cercle], 0)
        
        while 1:
            #calcul de l'angle de A (point de départ)
            tA = atan2(self.y-yO,self.x-xO)
            
            if (pas > 0 and r*tA+pas < r*tB) or (pas < 0 and r*tA+pas > r*tB):
                #nouveau point consigne : incrémenter l'abscisse curviligne de A du pas en mm
                #angle absolu pour C
                tC = tA + pas/r
                #coordonnées de C, prochain point consigne
                self.consigne_x = xO + r*cos(tC)
                self.consigne_y = yO + r*sin(tC)
                if self.config["mode_simulateur"]:
                    self.deplacements.simulateur.drawPoint(self.consigne_x,self.consigne_y,"green",False)
                
                #vérification des hooks
                for hook in hooks:
                    hook.evaluate()
                    
                #mise à jour des consignes en translation et rotation
                self._mise_a_jour_consignes()
                
                #acquittement du déplacement : sort de la boucle avec un return si arrivé ou bloqué
                acq = self._acquittement()
                if acq:
                    return acq
            else:
                self.log.debug("abscisse curviligne atteinte, on fixe la consigne au point d'arrivé")
                self.set_vitesse_rotation(1)
                #proche de la consigne, dernière mise à jour du point virtuel 
                self.consigne_x = xB
                self.consigne_y = yB
                
                #vérification des hooks
                for hook in hooks:
                    hook.evaluate()
                    
                acq = self._acquittement()
                if acq:
                    return acq
            
            sleep(1./self.frequence_maj_arc_de_cercle)
            
        
    def recaler(self):
        
        self.log.debug("début du recalage")
        
        print("on recule lentement jusqu'à bloquer sur le bord")
        self.set_vitesse_translation(1)
        self.set_vitesse_rotation(1)
        self.marche_arriere = True
        self.gestion_avancer(-1000)
        #input()
        print("on désactive l'asservissement en rotation pour se mettre parallèle au bord")
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.gestion_avancer(-300)
        #input()
        print("initialisation de la coordonnée x et de l'orientation")
        if self.couleur == "bleu":
            self.x = -self.config["table_x"]/2. + self.config["largeur_robot"]/2.
            self.orientation = 0.0
        else:
            self.x = self.config["table_x"]/2. - self.config["largeur_robot"]/2.
            self.orientation = pi
        #input()
        print("on avance doucement, en réactivant l'asservissement en rotation")
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.gestion_avancer(100)
        #input()
        print("on se tourne pour le deuxième recalage")
        self.gestion_tourner(pi/2)
        #input()
        print("on recule lentement jusqu'à bloquer sur le bord")
        self.marche_arriere = True
        self.gestion_avancer(-1000)
        #input()
        print("on désactive l'asservissement en rotation pour se mettre parallèle au bord")
        self.deplacements.desactiver_asservissement_rotation()
        self.set_vitesse_translation(2)
        self.gestion_avancer(-300)
        #input()
        print("initialisation de la coordonnée y et de l'orientation")
        self.y = self.config["largeur_robot"]/2.
        self.orientation = pi/2.
        #input()
        print("on avance doucement, en réactivant l'asservissement en rotation")
        self.marche_arriere = False
        self.deplacements.activer_asservissement_rotation()
        self.set_vitesse_translation(1)
        self.gestion_avancer(150)
        #input()
        print("on prend l'orientation initiale pour le match")
        self.gestion_tourner(pi)
        #input()
        print("vitesse initiales pour le match")
        self.set_vitesse_translation(2)
        self.set_vitesse_rotation(2)
       
        self.log.debug("recalage terminé")
        
    #############################################################################################################
    ### MÉTHODES DE DÉPLACEMENTS DE HAUT NIVEAU (TROUVÉES DANS LES SCRIPTS), AVEC RELANCES EN CAS DE PROBLÈME ###
    #############################################################################################################
    
    def gestion_avancer(self, distance, hooks=[]):
        retour = self.avancer(distance, hooks)
        if retour == 1:
            print("translation terminée !")
        elif retour == 2:
            self.stopper()
            print("translation arrêtée car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
        
    def gestion_tourner(self, angle, hooks=[]):
        
        if not self.marche_arriere:
            if self.couleur == "bleu":
                angle = pi - angle
                
        retour = self.tourner(angle, hooks)
        if retour == 1:
            print("rotation terminée !")
        elif retour == 2:
            self.stopper()
            print("rotation arrêtée car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
            
    def gestion_va_au_point(self, x, y, hooks=[], virage_initial=False):
        
        if self.couleur == "bleu":
            x *= -1
                
        retour = self.va_au_point(x, y, hooks, virage_initial)
        if retour == 1:
            print("point de destination atteint !")
        elif retour == 2:
            print("déplacement arrêté car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
            
    def gestion_arc_de_cercle(self,xM,yM,hooks=[]):
        
        if self.couleur == "bleu":
            xM *= -1
                
        retour = self.arc_de_cercle(xM,yM,hooks)
        if retour == 1:
            print("point de destination atteint !")
        elif retour == 2:
            print("déplacement arrêté car blocage !")
        elif retour == 3:
            self.stopper()
            print("capteurs !")
        
    def set_vitesse_translation(self, valeur):
        self.deplacements.set_vitesse_translation(valeur)
        self.vitesse_translation = int(valeur)
    
    def set_vitesse_rotation(self, valeur):
        self.deplacements.set_vitesse_rotation(valeur)
        self.vitesse_rotation = int(valeur)
