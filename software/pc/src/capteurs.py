#éventuelles importations nécessaires pour le module

class CapteursSerie():
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log

    def mesurer(self):
        """
        renvoi une distance, toussa...
        """
#        self.aze = "zer" #variable pour toute la classe
#        aze = "zer"	#variable pour la fonction
        
        self.log.debug("ca va")
        self.log.warning("probleme")
        self.log.critical("gros probleme")
        

        """
        pour PF : on utilise ici la méthode "communiquer" du service "serie" qui est en attribut de la classe Capteurs.
        elle prend trois arguments : 
          - la dénomination de la carte avec laquelle on communique (à paramétrer dans le constructeur de la classe Serie)
          - un tableau de messages d'envoi, qui seront séparés par des retours à la ligne
          - un entier spécifiant le nombre de lignes de retour attendues
        cette méthode renvoit un TABLEAU de STRING, contenant les lignes de retour.
        Donc on oublie pas de bien caster la sortie :)
        """

        nbValeurs=3 #le nombre de valeurs d'où est extraite la médiane. A passer en paramètre?
        valeurs=[] #cette liste contiendra les m valeurs
        for i in range(nbValeurs):
            retour = self.serie.communiquer("capteurs_actionneurs",["s"], 1)
            valeurs.append(int(retour[0]))

        valeurs.sort()	#les valeurs sont triées dans l'ordre croissant

        capteurUltrason=valeurs[m//2]

        valeurs=[]
        for i in range(nbValeurs): #idem, mais avec les infrarouges
            retour = self.serie.communiquer("capteurs_actionneurs",["i"], 1)
            valeurs.append(int(retour[0]))

        valeurs.sort()

        capteurInfrarouge=valeurs[m//2]

        self.log.debug("Appel capteurs et récupération de valeurs: OK")

        return max(capteurInfrarouge, capteurUltrason) #on retourne la distance maximale (on est optimiste)


class CapteursSimulateur():
    """
    classe gérant les capteurs (communication via la série avec la carte appropriée).
    """
    
    def __init__(self,simulateur,config,log):
        #services utilisés
        self.simulateur = simulateur
        self.config = config
        self.log = log

    def mesurer(self): 
        distance = self.simulateur.getRobotSensorValue()
        if distance==-1:
            return 5000
        else:
            return distance