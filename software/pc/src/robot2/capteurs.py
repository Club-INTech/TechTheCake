import math 

class Capteurs():
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        self.serie = serie
        self.config = config
        self.log = log
        
    def mesurer(self):
        try:
            us = int(self.serie.communiquer("capteurs_actionneurs",["us"], 1)[0])
            ir = int(self.serie.communiquer("capteurs_actionneurs",["ir"], 1)[0])
            return max(us,ir)
        except:
            # En cas d'erreur, on renvoie l'infini
            self.log.warning("Erreur de lecture des capteurs de proximité")
            return 3000
    
    def adverse_devant(self, robotX, robotY, robotO):
        distance = self.mesurer()
        if distance >= 0 and distance <= self.config["r2_distance_detection"]:
            #distance : entre le capteur situé à l'extrémité du robot et la facade du robot adverse
            distance_inter_robots = distance + self.config["rayon_robot_adverse"] + self.config["r2_epaisseur_avant"]
            x = robotX + distance_inter_robots * math.cos(robotO)
            y = robotY + distance_inter_robots * math.sin(robotO)
            
            #dans la table
            if x > (-self.config["table_x"]/2) and y > 0 and x < self.config["table_x"]/2 and y < self.config["table_y"]:
                # Vérifie que l'obstacle perçu n'est pas le gateau
                if not ((x-0)**2 + (y-2000)**2) < 550**2:
                    return True
        return False