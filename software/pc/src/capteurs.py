#éventuelles importations nécessaires pour le module

class Capteurs():
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
        
        
        
        
        """
        pour PF : on utilise ici la méthode "communiquer" du service "serie" qui est en attribut de la classe Capteurs.
        elle prend trois arguments : 
          - la dénomination de la carte avec laquelle on communique (à paramétrer dans le constructeur de la classe Serie)
          - un tableau de messages d'envoi, qui seront séparés par des retours à la ligne
          - un entier spécifiant le nombre de lignes de retour attendues
        cette méthode renvoit un TABLEAU de STRING, contenant les lignes de retour.
        Donc on oublie pas de bien caster la sortie :)
        """
        retour = self.serie.communiquer("capteurs_actionneurs",["mesurer"], 1)
        return int(retour[0])
    