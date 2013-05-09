import math
from outils_maths.point import Point

class Laser:
    
    def __init__(self, robot, serie, config, log):
        self.robot = robot
        self.serie = serie
        self.config = config
        self.log = log
        self.balises = [
            {"id": 0, "active": False},
            {"id": 1, "active": False}
        ]
        
    def balises_actives(self):
        """
        Indique les balises considérées comme opérationnelle pour le match
        """
        return [b for b in self.balises if b["active"]]
        
    def balises_ignorees(self):
        """
        Indique les balises considérées comme non opérationnelle pour le match
        """
        return [b for b in self.balises if not b["active"]]
    
    def allumer(self):
        """
        Allumer le moteur et les lasers
        """
        self.serie.communiquer("laser", ["motor_on"], 0)
        self.serie.communiquer("laser", ["laser_on"], 0)
        
    def eteindre(self):
        """
        Eteindre le moteur et les lasers
        """
        self.serie.communiquer("laser", ["laser_off"], 0)
        self.serie.communiquer("laser", ["motor_off"], 0)
        
    def verifier_balises_connectes(self):
        """
        Ping chaque balise et vérifie celles qui sont connectées
        """
        balises_ok = 0
        for balise in self.balises:
            if self.ping_balise(balise["id"]):
                if not balise["active"]:
                    balise["active"] = True
                    self.log.debug("balise n°" + str(balise["id"]) + " répondant au ping")
                balises_ok += 1
        return balises_ok
        
    def ping_balise(self, id_balise):
        """
        Ping une balise
        """
        ping = self.serie.communiquer("laser", ["ping_all"], len(self.balises))
        return ping[id_balise] != "aucune réponse"
#        return ping != ["NO_RESPONSE"]
        
    def frequence_moteur(self):
        """
        Récupère la fréquence actuelle du moteur
        """
        reponse = self.serie.communiquer("laser", ["freq"], 1)
        return float(reponse[0])
        
    def position_balise(self, id_balise):
        """
        Récupère la valeur (rayon, angle) d'une balise
        """
        # Récupération de la position de la balise dans le repère du robot
        reponse = self.serie.communiquer("laser", ["value", id_balise], 2)
        
        if reponse is None:
            return None
            
        if "NO_RESPONSE" in reponse:
            return None
            
        #if "NO_VALUE" in reponse:
            #return None
            
        if "OLD_VALUE" in reponse:
            return None
            
        if "UNVISIBLE" in reponse:
            return None
           
        # Fréquence actuelle du moteur
        freq = self.frequence_moteur()
        
        # Valeur de la distance, sur l'échelle du timer 8 bit
        timer = float(reponse[0])
        
        # Délai du passage des deux lasers, en seconde
        delai = 128 * timer / 20000000
        
        # Calcul de la distance (en mm)
        ecart_laser = 35
        theta = delai * freq * 2 * math.pi
        if theta == 0: 
            self.log.warning("Division par zéro dans le calcul d'angle : freq = {0}, delai = {1}".format(freq, delai))
            return None
            
        distance = ecart_laser / math.sin(theta / 2)
        
        # Angle
        angle = float(reponse[1])
        
        # Changement dans le repère de la table
        x = float(self.robot.x) + distance * math.cos(angle + self.robot.orientation)
        y = float(self.robot.y) + distance * math.sin(angle + self.robot.orientation)
        
        return Point(x, y)
        
    def verifier_coherence_balise(self):
        """
        Vérifie si les données des balises actives sont cohérentes en début de match
        """
        # Nombre d'essais pour les calculs
        essais = 10
        
        for balise in self.balises_actives():
            moyenne = 0.
            valeurs = []
            ecart_type = 0.
            n = 0
            for i in range(essais):
                reponse = self.serie.communiquer("laser", ["value", balise["id"]], 2)
                if not (reponse is None or "NO_RESPONSE" in reponse or "OLD_VALUE" in reponse or "UNVISIBLE" in reponse):
                    angle = float(reponse[1])
                    n += 1
                    moyenne += angle
                    valeurs.append(angle)
                                    
            # Calcul de la moyenne
            if n > 0:
                moyenne /= float(n)
                
                # Calcul de l'écart type
                for v in valeurs:
                    ecart_type += (v - moyenne) ** 2
                ecart_type /= float(n)
            
            # Vérification de la cohérence
            if n < essais / 2 or ecart_type > 1:
                self.log.warning("balise n°{0} ignorée pendant le match, valeurs renvoyées incohérentes (valeurs reçues = {1} / {2}, angle moyen = {3}, écart-type = {4})".format(balise["id"], n, essais, moyenne, ecart_type))
                self.balises[balise["id"]]["active"] = False
            else:
                self.log.debug("balise n°{0} renvoie des valeurs cohérentes (valeurs reçues = {1} / {2}, angle moyen = {3}, écart-type = {4})".format(balise["id"], n, essais, moyenne, ecart_type))
        
