from tests import ContainerTest
import math

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
        ping = self.serie.communiquer("laser", ["ping", str(id_balise)], 1)
        return ping != ["aucune réponse"]
        
    def frequence_moteur(self):
        """
        Récupère la fréquence actuelle du moteur
        """
        reponse = self.serie.communiquer("laser", ["freq"], 1)
        return reponse[0]
        
    def position_balise(self, id_balise):
        """
        Récupère la valeur (rayon, angle) d'une balise
        """
        # Récupération de la position de la balise dans le repère du robot
        reponse = self.serie.communiquer("laser", ["valeur", id_balise], 1)
        rayon = reponse[0]
        angle = reponse[1]
        
        # Changement dans le repère de la table
        x = float(self.robot.x) + rayon * math.cos(angle + self.robot.orientation)
        y = float(self.robot.y) + rayon * math.sin(angle + self.robot.orientation)
        
        return [x, y]

class TestLaser(ContainerTest):
    
    def setUp(self):
        pass

    def test_ok(self):
        self.assertTrue(True)
        
    def test_erreur(self):
        self.assertTrue(False)
