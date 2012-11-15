import abc


class Capteurs(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def mesurer(self,marche_arriere):
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

    def mesurer(self, marche_arriere): #cette méthode retourne une médiane d'un grand nombre de valeurs provenant des capteurs

        nbValeurs=3 #le nombre de valeurs d'où est extraite la médiane. A passer en paramètre?

        valeurs=[] #cette liste contiendra les m valeurs
        for i in range(nbValeurs):
            if(marche_arriere):
                retour = self.serie.communiquer("capteurs_actionneurs",["sAr"], 1)
            else:
                retour = self.serie.communiquer("capteurs_actionneurs",["sAv"], 1)
            valeurs.append(int(retour[0]))

        valeurs.sort()	#les valeurs sont triées dans l'ordre croissant

        capteurUltrason=valeurs[nbValeurs//2]

        valeurs=[]
        for i in range(nbValeurs): #idem, mais avec les infrarouges
            if(marche_arriere): 
                retour = self.serie.communiquer("capteurs_actionneurs",["iAr"], 1)
            else:
                retour = self.serie.communiquer("capteurs_actionneurs",["iAv"], 1)
            valeurs.append(int(retour[0]))

        valeurs.sort()

        capteurInfrarouge=valeurs[nbValeurs//2]

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

    def mesurer(self,marche_arriere): 
        distance = self.simulateur.getRobotSensorValue()
        if distance==-1:
            return 5000
        else:
            return distance
