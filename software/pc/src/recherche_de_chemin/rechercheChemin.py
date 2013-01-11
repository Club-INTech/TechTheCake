class RechercheChemin:
    
    def __init__(self,table,config,log):
        self.table = table
        self.config = config
        self.log = log

    def get_chemin(self,depart,arrivee):
        self.log.debug("calcul du chemin de "+str(depart)+" vers "+str(arrivee)+".")
        return [(depart+arrivee)*0.5,arrivee]