
class DeplacementsSerie:
    """
    classe gérant les envoi sur la série de la carte d'asservissement.
    hérite de la classe SerialManager
    """
    def __init__(self,serie,config,log):
        self.serie = serie
        self.config = config
        self.log = log
        
        self.vitesse_translation = 2
        self.vitesse_rotation = 2

    def changer_vitesse_translation(self, valeur):
        """
        spécifie une vitesse prédéfinie en translation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        #definition des constantes d'asservissement en fonction de la vitesse
        kp_translation = [0.75,0.75,0.5]
        kd_translation = [2.0,2.5,4.0]
        vb_translation = [60,100,200]
        
        envoi = ["ctv"]
        envoi.append(float(kp_translation[valeur-1]))
        envoi.append(float(kd_translation[valeur-1]))
        envoi.append(int(vb_translation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
        
        #sauvegarde de la valeur choisie
        self.vitesse_translation = int(valeur)
        
    def changer_vitesse_rotation(self, valeur):
        """
        spécifie une vitesse prédéfinie en rotation
        une valeur 1,2,3 est attendue
        1 : vitesse "prudente"
        2 : vitesse normale
        3 : vitesse pour forcer
        """
        
        #definition des constantes d'asservissement en fonction de la vitesse
        kp_rotation = [1.5,1.2,0.9]
        kd_rotation = [2.0,3.5,3.5]
        vb_rotation = [80,100,200]
        
        envoi = ["crv"]
        envoi.append(float(kp_rotation[valeur-1]))
        envoi.append(float(kd_rotation[valeur-1]))
        envoi.append(int(vb_rotation[valeur-1]))
        self.serie.communiquer("asservissement",envoi, 0)
            
        #sauvegarde de la valeur choisie
        self.vitesse_rotation = int(valeur)
        
    def avancer(self, distance):
        """
        Fonction de script pour faire avancer le robot en ligne droite. (distance <0 => reculer)
        :param distance: Distance à parcourir
        :type angle: Float
        """
        
        envoi = ["d"]
        envoi.append(float(distance))
        self.serie.communiquer("asservissement",envoi, 0)
        
        #pour redémarrer la gestion_stoppage : le robot n'est plus considéré à l'arret
        #TODO : récupérer cet attribut de Asservissement
        self.est_stoppe = False

        
class Deplacements_simu:

    def __init__(self,config,log):
        self.config = config
        self.log = log
        
    def parle(self):
        print("déplacements pour la simulation")