import time

class Serie:
    """
    Redirige les requêtes au service `serie` vers la série réelle (communication robot) ou la série de simulation.
    """
    
    def __init__(self, serieReelle, serieSimulation, config, log):
        
        self.serieReelle = serieReelle
        self.serieSimulation = serieSimulation
        self.log = log
        self.config = config
        
        #dictionnaire des périphériques nécessaires : 
        #contient des tuples (données pour la série réelle, données pour la simulation)
        self.dico_infos_peripheriques = {
            "asservissement": ((0,9600),"deplacements"),
            "capteurs_actionneurs" : ((3,9600),"capteurs_actionneurs"),
            "laser" : ((4,38400),"laser"),
            "ascenseur": ((2,9600),"ascenseur")
        }
        
        if not self.serieReelle is None:
            #attribution initiale des périphériques série réels
            self.serieReelle.definir_peripheriques(self.dico_infos_peripheriques)
            self.serieReelle.attribuer()
            
        if not self.serieSimulation is None:
            #attribution initiale des périphériques série virtuels
            self.serieSimulation.definir_peripheriques(self.dico_infos_peripheriques)
        
        self.arret_serie=False
        
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        if not self.arret_serie:
            
            #instance réelle ou simulée de la série, pour un destinataire donné
            if destinataire in self.config["cartes_serie"]:
                serie = self.serieReelle
            elif destinataire in self.config["cartes_simulation"]:
                serie = self.serieSimulation
            
            try:
                reponse = serie.communiquer(destinataire, messages, nb_lignes_reponse)
                assert reponse is not None
                assert len(reponse) == nb_lignes_reponse
                return reponse
            except AssertionError:
                self.log.warning("La trame réponse de "+str(destinataire)+" à "+str(messages)+" est mauvaise ! Renvoi...")
                time.sleep(0.01)
                return self.communiquer(destinataire, messages, nb_lignes_reponse)
            except:
                self.log.critical("La carte '"+destinataire+"' n'est ni en simulation ni sur la série !")
                raise Exception

    def serie_prete(self):
        return self.serieReelle is None or self.serieReelle.serie_prete()
    
    def set_arret_serie(self):
        """
        Méthode pour arrêter le service série, appelée par le service timer à la fin du match.
        """
        self.arret_serie=True
