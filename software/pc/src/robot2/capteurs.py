
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
            us = int(self.serie.communiquer("capteurs_actionneurs",["us"], 1))
            ir = int(self.serie.communiquer("capteurs_actionneurs",["ir"], 1))
            return max(us,ir)
        except:
            # En cas d'erreur, on renvoie l'infini
            self.log.warning("Erreur de lecture des capteurs de proximité")
            return 3000