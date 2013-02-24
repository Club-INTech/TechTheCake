from time import sleep,time
from scripts import *
import robot

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

        self.note = {}

        for key in self.scripts.keys():
            self.note[key] = 0

#        if self.config["ennemi_fait_toutes_bougies"]: #à décommenter une fois que le script bougies sera fini
#            del self.scripts["ScriptBougies"]
            
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
            self._maj_script()
            self.rechercheChemin.preparer_environnement()

            for script in self.scripts:
                liste_versions = self.scripts[script].versions()
                for version in liste_versions:
                    self.log.debug("Notation du script "+script)
                    self.note[script]=self._noter_script(script, self.scripts[script].point_entree(version))
                    self.log.debug("Note du script "+script+": "+str(self.note[script]))

            noteInverse = dict(map(lambda item: (item[1],item[0]),self.note.items()))
            scriptAFaire=noteInverse[max(noteInverse.keys())]   #ce script a reçu la meilleure note

            self.log.debug("STRATÉGIE FAIT: "+scriptAFaire)
            if not self.timer.get_fin_match():
                try:
                    self.scripts[scriptAFaire].agit(1)
                except robot.ExceptionMouvementImpossible:
                    self.log.warning("Mouvement impossible lors du script: "+scriptAFaire)
                    
    
            sleep(0.1)
        self.log.debug("Arrêt de la stratégie.")

    """
    Met à jour les points et retire les scripts qui ne peuvent plus en rapporter
    """
    def _maj_script(self):

        if "ScriptBougies" in self.scripts and self.scripts["ScriptBougies"].score()==0:
            del self.script["ScriptBougies"]
            del self.note["ScriptBougies"]

        if "ScriptRecupererVerres" in self.scripts and self.scripts["ScriptRecupererVerres"].score()==0:
            del self.script["ScriptRecupererVerres"]
            del self.note["ScriptRecupererVerres"]

        if "ScriptCadeaux" in self.scripts and self.scripts["ScriptCadeaux"].score()==0:
            del self.script["ScriptCadeaux"]
            del self.note["ScriptCadeaux"]

        if "ScriptDeposerVerres" in self.scripts and "ScriptRecupererVerres" in self.scripts and self.scripts["ScriptDeposerVerres"].score()==0 and self.scripts["ScriptRecupererVerres"].score()==0:
            del self.script["ScriptDeposerVerres"]
            del self.note["ScriptDeposerVerres"]

    """
    Note un script (en fonction du nombre de points qu'il peut rapporter, de la position de l'ennemi et de sa durée)
    """
    def _noter_script(self, script, point_entree):
        dureeScript=self.scripts[script].calcule(1)+1    #au cas où, pour éviter une division par 0... (ce serait vraiment dommage!)

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
            distanceE=self._distance_ennemi(point_entree)+1 #le +1 est pour empêcher la division par 0
            try:
                return 1000000000*(self.scripts[script].score())/(dureeScript*dureeScript*dureeScript*distanceE*distanceE)
            except ZeroDivisionError:
                self.log.critical("Division par zéro dans le calcul de la note! :o") #sait-on jamais... je préfère ne pas prendre le risque de voir le robot se paralyser bêtement
                return self.scripts[script].score()


    def _distance_ennemi(self, point_entree): #on prend la distance euclidienne, à vol d'oiseau. Attention, on prend le min: cette valeur est sensible aux mesures aberrantes
        distance_min=3000 #une distance très grande, borne sup de la valeur renvoyée.

        for obstacle in self.table.obstacles():
            d = point_entree.distance(obstacle.position)
            if d < distance_min:
                distance_min = d

        return distance_min

