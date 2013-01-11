import abc


class Capteurs(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def mesurer(self,marche_arriere):
        pass

    def _fusion(self, capteur_values): #on renvoie le max (5000 si aucune valeur)
        if capteur_values==[]:
            return 5000
        else:
            return sorted(capteur_values, reverse=True)[0]
            
    @abc.abstractmethod
    def demarrage_match(self):
        pass

class CapteursSerie(Capteurs):
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        try:
            self.nb_capteurs_infrarouge_avant=int((self.serie.communiquer("capteurs_actionneurs",["nbI"], 1))[0])
            self.nb_capteurs_infrarouge_arriere=int((self.serie.communiquer("capteurs_actionneurs",["nbi"], 1))[0])
            self.nb_capteurs_ultrason_avant=int((self.serie.communiquer("capteurs_actionneurs",["nbS"], 1))[0])
            self.nb_capteurs_ultrason_arriere=int((self.serie.communiquer("capteurs_actionneurs",["nbs"], 1))[0])

            self.log.debug("Il y a ", self.nb_capteurs_infrarouge_avant, "capteurs infrarouge à l'avant, ", self.nb_capteurs_infrarouge_arriere, "à l'arrière.")
            self.log.debug("Il y a ", self.nb_capteurs_ultrason_avant, "capteurs ultrason à l'avant, ", self.nb_capteurs_ultrason_arriere, "à l'arrière.")
        except:
            self.log.warning("la carte capteur n'a pas été atteinte lors de la construction du service")

    def mesurer(self, marche_arriere=False):

        if marche_arriere:
            capteur_values = self.serie.communiquer("capteurs_actionneurs",["s"], self.nb_capteurs_ultrason_arriere)
        else:
            capteur_values = self.serie.communiquer("capteurs_actionneurs",["S"], self.nb_capteurs_ultrason_avant)

        if marche_arriere:
            capteur_values = capteur_values + self.serie.communiquer("capteurs_actionneurs",["i"], self.nb_capteurs_infrarouge_arriere)
        else:
            capteur_values = capteur_values + self.serie.communiquer("capteurs_actionneurs",["I"], self.nb_capteurs_infrarouge_avant)

        self.log.debug("Appel capteurs et récupération de valeurs: OK")

        return self._fusion(capteur_values)

    def demarrage_match(self):
        #TODO : jumper
        return True

class CapteursSimulateur(Capteurs):
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,simulateur,config,log):
        #services utilisés
        self.simulateur = simulateur
        self.config = config
        self.log = log
        
        #definition des zones des capteurs
        self.simulateur.addSensor(0,{"list":[{"int":[0,-400]},{"int":[-135.,-1100.]},{"int":[135,-1100]}]}) #nombre pair: infrarouge. Nombre impair: ultrasons
        self.simulateur.addSensor(2,{"list":[{"int":[0,400]},{"int":[-135.,1100.]},{"int":[135,1100]}]})
        self.simulateur.addSensor(1,{"list":[{"int":[0,-400]},{"int":[-600.,-1600.]},{"int":[600,-1600]}]})
        self.simulateur.addSensor(3,{"list":[{"int":[0,400]},{"int":[-600.,1600.]},{"int":[600,1600]}]})

    def mesurer(self,marche_arriere=False):
        if marche_arriere:
            distance = [self.simulateur.getSensorValue(0),self.simulateur.getSensorValue(1)]
        else:
            distance = [self.simulateur.getSensorValue(2),self.simulateur.getSensorValue(3)]

        return self._fusion(distance)

    def demarrage_match(self):
        return True
