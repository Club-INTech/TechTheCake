from time import sleep,time
from scripts import *

class Strategie:
    """
    Classe gérant l'intelligence artificielle.
    Son rôle est de noter différents scripts (selon leur durée, la distance d'un ennemi, ...) et de choisir le plus avantageux. C'est également cette classe qui fait les appels d'ajout d'obstacle à la recherche de chemin.
    """
    def __init__(self, robot, scripts, rechercheChemin, table, timer, config, log): #retirer robot

        self.robot = robot
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log
        self.scripts = scripts

        self.arguments = {"ScriptBougies": 1, "ScriptCadeaux": 1, "ScriptRecupererVerres": (), "ScriptDeposerVerres": (), "ScriptCasserTour": ()}
        self.liste_points_entree = ["cadeau", "verreNous", "verreEnnemi", "Pipeau"]
        self.points={}
        self.note={}

        for key in self.scripts.keys():
            self.points[key] = 0
            self.note[key] = 0
        if self.config["ennemi_fait_toutes_bougies"]:
            del self.scripts["ScriptBougies"]
            
    """
    Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
    """
    def boucle_strategie(self):
        """
        Boucle principale de la stratégie. 
        """
        self.log.debug("Stratégie lancée.")

        while not self.timer.get_fin_match():
#            self.rechercheChemin.retirer_obstacles_dynamique();
            self._initialiser_points()
            self.rechercheChemin.preparer_environnement()

            for script in self.scripts:
            #deuxième boucle sur tous les points entrées
                if self.points[script]!=0:
                    self.log.debug("Notation du script "+script)
                    note[script]=self._noter_script(script)
                    self.log.debug("Note du script "+script+": "+str(note[script]))

                    
            noteInverse = dict(map(lambda item: (item[1],item[0]),note.items()))
            scriptAFaire=noteInverse[max(noteInverse.keys())]   #ce script a reçu la meilleure note

            self.log.debug("STRATÉGIE FAIT: "+scriptAFaire)
            if not self.timer.get_fin_match():
                self.scripts[scriptAFaire].agit(self.arguments[scriptAFaire])
    
            sleep(0.1)
        self.log.debug("Arrêt de la stratégie.")

    """
    Met à jour les points et retire les scripts qui ne peuvent plus en rapporter
    """
    def _initialiser_points(self):
        if "ScriptBougies" in self.scripts:
            self.points["ScriptBougies"]=0
            for element in self.table.bougies:
                if not element["couleur"]=="red" and not element["traitee"]: #la condition sur la couleur est pipeau
                    self.points["ScriptBougies"]+=4
                if self.points["ScriptBougies"]==0:
                    del self.script["ScriptBougies"]
        if "ScriptRecupererVerres" in self.scripts:
            for element in self.table.verres:
                if element["present"]:       #à pondérer si l'ascenseur est plutôt plein ou plutôt vide
                    self.points["ScriptRecupererVerres"]+=6 #à tirer vers le haut pour les faire en début de partie (et ensuite baisser les points par incertitude?)
                if self.points["ScriptRecupererVerres"]==0:
                    del self.script["ScriptRecupererVerres"]
        if "ScriptCadeaux" in self.scripts:
            self.points["ScriptCadeaux"]=0
            for element in self.table.cadeaux:
                if not element["ouvert"]:
                    self.points["ScriptCadeaux"]+=4
                if self.points["ScriptCadeaux"]==0:
                    del self.script["ScriptCadeaux"]
        if "ScriptDeposerVerres" in self.scripts:
            self.points["ScriptDeposerVerres"]=4*max(self.robot.nb_verres_avant*(self.robot.nb_verres_avant+1)/2,self.robot.nb_verres_arriere*(self.robot.nb_verres_arriere+1)/2)
            if self.points["ScriptDeposerVerres"]==0 and self.points["ScriptRecupererVerres"]==0:
                del self.script["ScriptDeposerVerres"]
        if "ScriptCasserTour" in self.scripts:
            self.points["ScriptCasserTour"]=(time()-self.timer.get_date_debut())    #à revoir

    """
    Note un script (en fonction du nombre de points qu'il peut rapporter, de la position de l'ennemi et de sa durée)
    """
    def _noter_script(self, script):
        dureeScript=self.scripts[script].calcule(self.arguments[script])+1    #au cas où, pour éviter une division par 0... (ce serait vraiment dommage!)

        #normalement ce cas n'arrive plus
        if dureeScript<=0:
            self.log.warning(script+" a un temps d'exécution négatif!")
            dureeScript=1

        #pour prendre les verres, on ajoute à durée script le temps de déposer les verres
        if script=="ScriptRecupererVerres" and dureeScript+deposer_verre.calcule()>(self.config["temps_match"]-time()+self.timer.get_date_debut()):
            self.log.critical("Plus le temps de prendre des verres, on n'aurait pas le temps de les déposer.")
            return 0
        elif not dureeScript<(self.config["temps_match"]-time()+self.timer.get_date_debut()): #si on a le temps de faire l'action avant la fin du match
            self.log.critical("Plus le temps d'exécuter "+script)
            return 0
        else:
            distanceE=self._distance_ennemi(script)+1              #idem
            try:
                return 1000000000*(self.points[script])/(dureeScript*dureeScript*dureeScript*distanceE*distanceE)
            except ZeroDivisionError:
                self.log.critical("Division par zéro dans le calcul de la note! :o") #sait-on jamais... je préfère ne pas prendre le risque de voir le robot se paralyser bêtement
                return self.points[script]


    def _distance_ennemi(self, script): #on prend la distance euclidienne, à vol d'oiseau. Attention, on prend le min: cette valeur est sensible aux mesures aberrantes
        distance_min=3000 #une distance très grande, borne sup de la valeur renvoyée.
        for obstacle in self.table.obstacles():
            if Point.distance(self.scripts[script].point_entree(),obstacle.position.x)<distance_min:
                distance_min=d
        return distance_min

#TODO
#retirer du dictionnaire des scripts ceux déjà fait (entièrement)
