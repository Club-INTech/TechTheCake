
class Capteurs():
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        self.serie = serie
        self.config = config
        self.log = log
        
        self.capteurs_avant_actifs = True
        self.capteurs_arriere_actifs = True
        
        """
        try:
            # Récupération du nombre de capteurs
            self.nb_capteurs_infrarouge_avant = int(self.serie.communiquer("capteurs_actionneurs",["nbI"], 1)[0])
            self.nb_capteurs_infrarouge_arriere = int(self.serie.communiquer("capteurs_actionneurs",["nbi"], 1)[0])
            self.nb_capteurs_ultrason_avant = int(self.serie.communiquer("capteurs_actionneurs",["nbS"], 1)[0])
            self.nb_capteurs_ultrason_arriere = int(self.serie.communiquer("capteurs_actionneurs",["nbs"], 1)[0])
            self.log.debug("Il y a " + str(self.nb_capteurs_infrarouge_avant) + " capteurs infrarouge à l'avant, " + str(self.nb_capteurs_infrarouge_arriere) + " à l'arrière.")
            self.log.debug("Il y a " + str(self.nb_capteurs_ultrason_avant) + " capteurs ultrason à l'avant, " + str(self.nb_capteurs_ultrason_arriere) + " à l'arrière.")
        except Exception as e:
            self.log.critical(e)#"La carte capteur n'a pas été atteinte lors de la construction du service.")
        """
        self.nb_capteurs_infrarouge_avant = 1
        self.nb_capteurs_infrarouge_arriere = 1
        self.nb_capteurs_ultrason_avant = 1
        self.nb_capteurs_ultrason_arriere = 1
        
    def mesurer(self, marche_arriere=False):

        try:
            if marche_arriere:
                capteur_values = self.serie.communiquer("capteurs_actionneurs",["us_arr"], self.nb_capteurs_ultrason_arriere)
                if self.capteurs_arriere_actifs:
                    capteur_values += self.serie.communiquer("capteurs_actionneurs",["ir_arr"], self.nb_capteurs_infrarouge_arriere)
            else:
                capteur_values = self.serie.communiquer("capteurs_actionneurs",["us_av"], self.nb_capteurs_ultrason_avant)
                if self.capteurs_avant_actifs:
                    capteur_values += self.serie.communiquer("capteurs_actionneurs",["ir_av"], self.nb_capteurs_infrarouge_avant)

            capteur_values = [int(i) for i in capteur_values]
            
            return sorted(capteur_values, reverse=True)[0]
        except Exception as e:
            # En cas d'erreur, on renvoie l'infini
            self.log.warning(e)
            return 3000
                
    def desactiver_capteurs_avant(self):
        self.log.debug("Capteurs Sharp avant désactivés")
        self.capteurs_avant_actifs = False
    def activer_capteurs_avant(self):
        self.log.debug("Capteurs Sharp avant activés")
        self.capteurs_avant_actifs = True
    def desactiver_capteurs_arriere(self):
        self.log.debug("Capteurs Sharp arrière désactivés")
        self.capteurs_arriere_actifs = False
    def activer_capteurs_arriere(self):
        self.log.debug("Capteurs Sharp arrière activés")
        self.capteurs_arriere_actifs = True

    def demarrage_match(self):
        try:
            return self.serie.communiquer("capteurs_actionneurs",["j"], 1)[0] == "0"
        except Exception as e:
            self.log.warning("Erreur de lecture du jumper : "+str(e))
        
    def verre_present(self, avant):
        try:
            if avant:
                return int(self.serie.communiquer("capteurs_actionneurs",["cap_asc_av"], 1)[0])!=0
            else:
                return int(self.serie.communiquer("capteurs_actionneurs",["cap_asc_arr"], 1)[0])!=0
        except:
            self.log.warning("Erreur de lecture des capteurs de verres")
            return False
