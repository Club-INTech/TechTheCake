import abc


class Capteurs(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def mesurer(self,marche_arriere):
        pass
    def _fusion(self, valeur1, valeur2):
        return max(valeur1, valeur2)
    

class CapteursSerie(Capteurs):
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        self.nb_capteurs_infrarouge_avant=int((self.serie.communiquer("capteurs_actionneurs",["nbI"], 1))[0])
        self.nb_capteurs_infrarouge_arriere=int((self.serie.communiquer("capteurs_actionneurs",["nbi"], 1))[0])
        self.nb_capteurs_ultrason_avant=int((self.serie.communiquer("capteurs_actionneurs",["nbS"], 1))[0])
        self.nb_capteurs_ultrason_arriere=int((self.serie.communiquer("capteurs_actionneurs",["nbs"], 1))[0])
        

#cette méthode retourne une médiane d'un grand nombre de valeurs provenant des capteurs
    def mesurer(self, marche_arriere=False):

        if marche_arriere:
            if self.nb_capteurs_ultrason_avant>=1:
                capteurUltrason = int((self.serie.communiquer("capteurs_actionneurs",["S"], self.nb_capteurs_ultrason_avant))[0])
            else:
                capteurUltrason = 5000
        else:
            if self.nb_capteurs_ultrason_arriere>=1:
                capteurUltrason = int((self.serie.communiquer("capteurs_actionneurs",["s"], self.nb_capteurs_ultrason_arriere))[0])
            else:
                capteurUltrason = 5000

        if marche_arriere:
            if self.nb_capteurs_infrarouge_avant>=1:
                capteurInfrarouge = int((self.serie.communiquer("capteurs_actionneurs",["I"], self.nb_capteurs_infrarouge_avant))[0])
            else:
                capteurInfrarouge = 5000
        else:
            if self.nb_capteurs_infrarouge_arriere>=1:
                capteurInfrarouge = int((self.serie.communiquer("capteurs_actionneurs",["i"], self.nb_capteurs_infrarouge_arriere))[0])
            else:
                capteurInfrarouge = 5000

        self.log.debug("Appel capteurs et récupération de valeurs: OK")

        return max(capteurInfrarouge, capteurUltrason) #on retourne la distance maximale (on est optimiste)


class CapteursSimulateur(Capteurs):
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,simulateur,config,log):
        #services utilisés
        self.simulateur = simulateur
        self.config = config
        self.log = log

    def mesurer(self,marche_arriere=False):
        if marche_arriere:
            distance = self.simulateur.getSensorValue(0)
        else:
            distance = self.simulateur.getSensorValue(1)
        if distance==-1:
            return 5000
        else:
            return distance
