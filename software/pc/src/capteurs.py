class Capteurs():
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        try:
            self.nb_capteurs_infrarouge_avant=int(self.serie.communiquer("capteurs_actionneurs",["nbI"], 1)[0])
            self.nb_capteurs_infrarouge_arriere=int(self.serie.communiquer("capteurs_actionneurs",["nbi"], 1)[0])
            self.nb_capteurs_ultrason_avant=int(self.serie.communiquer("capteurs_actionneurs",["nbS"], 1)[0])
            self.nb_capteurs_ultrason_arriere=int(self.serie.communiquer("capteurs_actionneurs",["nbs"], 1)[0])

            self.log.debug("Il y a "+str(self.nb_capteurs_infrarouge_avant)+"capteurs infrarouge à l'avant, "+str(self.nb_capteurs_infrarouge_arriere)+"à l'arrière.")
            self.log.debug("Il y a "+str(self.nb_capteurs_ultrason_avant)+"capteurs ultrason à l'avant, "+str(self.nb_capteurs_ultrason_arriere)+"à l'arrière.")
        except Exception as e:
            self.log.warning("la carte capteur n'a pas été atteinte lors de la construction du service")
            print(e)
            input()
            
    def _fusion(self, capteur_values): #on renvoie le max (5000 si aucune valeur)
        if capteur_values==[]:
            return 5000
        else:
            return sorted(capteur_values, reverse=True)[0]
            
    def mesurer(self, marche_arriere=False):

        if marche_arriere:
            capteur_values = self.serie.communiquer("capteurs_actionneurs",["s"], self.nb_capteurs_ultrason_arriere)
        else:
            capteur_values = self.serie.communiquer("capteurs_actionneurs",["S"], self.nb_capteurs_ultrason_avant)

        if marche_arriere:
            capteur_values = capteur_values + self.serie.communiquer("capteurs_actionneurs",["i"], self.nb_capteurs_infrarouge_arriere)
        else:
            capteur_values = capteur_values + self.serie.communiquer("capteurs_actionneurs",["I"], self.nb_capteurs_infrarouge_avant)

        return self._fusion(capteur_values)

    def lire_couleur(self):
        result = self.serie.communiquer("capteur_couleur",["c"],1)[0]
        if result == "indecis":
            result = "bleu"
        return result

    def demarrage_match(self):
        #TODO : jumper
        return True
