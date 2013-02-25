from mutex import Mutex
import random
import math

################################################################################
#####  PROTOCOLE VIRTUEL POUR SIMULATION DE LA SERIE SUR LES DEPLACEMENTS  #####
################################################################################
class ProtocoleVirtuelDeplacements:
   
    def __init__(self,simulateur, log):
        self.simulateur = simulateur
        self.log = log
        
    def d(self, distance):
        self.simulateur.moveRobot(distance)
        return []

    def t(self, angle):
        last = round(self.simulateur.getAngle(),4)
        if not angle == last:
            self.simulateur.turnRobot(angle, True)
        return []
    
    def stop(self):
        self.simulateur.stopRobot()
        return []  
            
    def cx(self, new_x):
        self.simulateur.setRobotPosition(new_x, self.simulateur.getY())
        return []
    
    def cy(self, new_y):
        # le +1 est un pur hack sachant qu'on se recale sur y=0.BONJOUR MARC !!
        self.simulateur.setRobotPosition(self.simulateur.getX(), new_y+1)
        return []
    
    def co(self, new_o):
        self.simulateur.setRobotAngle(new_o)
        return []

    def ct1(self):
        return []
        
    def cr1(self):
        return []
        
    def ct0(self):
        return []
        
    def cr0(self):
        return []
    
    def ctv(self, *useless):
        return []
    
    def crv(self, *useless):
        return []
    
    def infos(self):
        #dépassement du seuil de tolérance pour l'immobilité du robot
        if self.simulateur.isMoving() or self.simulateur.isTurning():
            erreur = 1000
        else:
            erreur = 0
            
        if self.simulateur.isBlocked(): 
            pwm = 1000
        else: 
            pwm = 0
    
        return [pwm, pwm, erreur, erreur]
        
    def xyo(self):
        return [self.simulateur.getX(), self.simulateur.getY(), int(self.simulateur.getAngle()*1000)]
            
################################################################################
#####  PROTOCOLE VIRTUEL POUR SIMULATION DE LA SERIE SUR LES CAPTEURS      #####
################################################################################
class ProtocoleVirtuelCapteurs:
   
    def __init__(self,simulateur, log):
        self.simulateur = simulateur
        self.log = log
        
    def nbs(self):
        #nombre de capteurs ultrasons à l'arrière
        return [1]
        
    def nbS(self):
        #nombre de capteurs ultrasons à l'avant
        return [1]
        
    def nbi(self):
        #nombre de capteurs infrarouges à l'arrière
        return [1]
        
    def nbI(self):
        #nombre de capteurs infrarouges à l'avant
        return [1]
    
    def s(self):
        #capteurs ultrasons de l'arrière
        return [self._valeur_capteur(3)]
        
    def S(self):
        #capteurs ultrasons de l'avant
        return [self._valeur_capteur(2)]
        
    def i(self):
        #capteurs infrarouges de l'arrière
        return [self._valeur_capteur(1)]
        
    def I(self):
        #capteurs infrarouges de l'avant
        return [self._valeur_capteur(0)]

    def c(self):
        #TODO
        return ["rouge"]

    def demarrage_match(self):
        return [True]
        
    def _valeur_capteur(self, id):
        valeur = self.simulateur.getSensorValue(id)
        return valeur if valeur >= 0 else 5000
        
################################################################################
#####  PROTOCOLE VIRTUEL POUR SIMULATION DE LA SERIE SUR LES ACTIONNEURS   #####
################################################################################
class ProtocoleVirtuelActionneurs:
    
    def __init__(self,simulateur, log):
        self.simulateur = simulateur
        self.log = log
        
    def g(self,*useless) :
        return []
    
    def gonfler_ballon(self) :
        return []

    def haut(self,*useless) :
        return []
    
    def bas(self,*useless) :
        return []
    
    def changerConstantes(self, *useless):
        return []
        
################################################################################
#####  PROTOCOLE VIRTUEL POUR SIMULATION DE LA SERIE SUR LA BALISE LASER   #####
################################################################################
class ProtocoleVirtuelLaser:
    
    def __init__(self, simulateur, log):
        self.simulateur = simulateur
        self.log = log
        
    def laser_on(self):
        #self.simulateur.log("Allumage des lasers")
        return []
        
    def motor_on(self):
        return []
    
    def laser_off(self):
        #self.simulateur.log("Extinction des lasers") 
        return []
        
    def motor_off(self):
        return []
    
    def freq(self):
        return ["18"]
        
    def ping(self, id_balise):
        try:
            self.simulateur.getEnemyPositionFromRobot(id_balise)
            return ["ping"]
        except Exception:
            return ["NO_RESPONSE"]
        
    def value(self, id_balise):
        position_reelle = self.simulateur.getEnemyPositionFromRobot(id_balise)
        distance = position_reelle[0] + random.gauss(0,15)
        angle = position_reelle[1] + random.gauss(0,0.025)
        
        # Valeur fausse random
        if random.randint(0, 15) == 0:
            angle = random.uniform(-math.pi, math.pi)
        
        ecart_laser = 35
        freq = 18
        
        # Cas où la balise est très proche du robot
        # Provoque un overflow du timer sur la balise
        if distance < 300:
            distance = 2000
        
        theta = 2 * math.asin(ecart_laser / distance)
        delai = theta / (2 * math.pi * freq)
        timer = 20000000 * delai / 128
        
        return [timer, angle]

################################################################################
#####  CLASSE DE SERIE EN SIMULATION : UTILISE DES PERIPHERIQUES VIRTUELS  #####
################################################################################
class SerieSimulation:
    """
    Permet de simuler des échanges série avec des périphériques de simulation. 
    Implémente la méthode communiquer de facon strictement identique (voir la classe Serie), avec memes appels et retours.
    """
    
    def __init__(self, simulateur, log):
        
        #instances des dépendances
        self.log = log
        
        #mutex évitant les écritures/lectures simultanées sur la série
        self.mutex = Mutex()
        
        self.deplacements = ProtocoleVirtuelDeplacements(simulateur, log)
        self.actionneurs = ProtocoleVirtuelActionneurs(simulateur, log)
        self.capteurs = ProtocoleVirtuelCapteurs(simulateur, log)
        self.laser = ProtocoleVirtuelLaser(simulateur, log)
        
    def definir_peripheriques(self, dico_infos_peripheriques):
        #dictionnaire des périphériques de simulation à partir des données fournies
        self.peripheriques = dict(map(lambda c: (c[0],getattr(self, c[1][1])),dico_infos_peripheriques.items()))
        
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        """
        Méthode de communication avec des périphériques simulés. 
        Le destinataire est une classe. 
        Le premier pattern du message (protocole) est une méthode. 
        Les autres composants du messages sont envoyés en tant qu'arguments. 
        Communiquer renvoit également la réponse sous forme d'une liste (idem classe Serie).
        
        Une liste messages d'un seul élément : ["chaine"] peut éventuellement être remplacée par l'élément simple : "chaine".  #userFriendly
        """
        if not type(messages) is list:
            #permet l'envoi d'un seul message, sans structure de liste
            messages = [messages]
        
        #Utilisation du protocole série sur le périphérique virtuel. Renvoit une liste de réponses, éventuellement vide.
        method = messages[0].replace("?","")
        args = tuple(messages[1:])
        
        try:
            reponses = getattr(self.peripheriques[destinataire], method)(*args)
            return reponses
        except Exception as e:
            self.log.critical("Erreur renvoyée par le simulateur : \"" + str(e) + "\" lors de l'envoi de '"+method+"' à '"+destinataire+"'.")
                
