from time import sleep,time
from scripts import *
import robot

class Strategie:
    """
    Classe gérant l'intelligence artificielle.
    Son rôle est de noter différents scripts (selon leur durée, la distance d'un ennemi, ...) et de choisir le plus avantageux. 
    C'est également cette classe qui fait les appels d'ajout d'obstacle à la recherche de chemin.
    """
    def __init__(self, scripts, rechercheChemin, table, timer, config, log):

        self.scripts = scripts
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log
        
        self.echecs = {}

        if self.config["ennemi_fait_toutes_bougies"]: #à décommenter une fois que le script bougies sera fini
            self.log.warning("Comme l'ennemi fait toutes les bougies, on ne les fera pas.")
            del self.scripts["ScriptBougies"]

    def boucle_strategie(self):

        while not self.timer.match_demarre:
            sleep(.5)
        """
        Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
        """
        self.log.debug("Stratégie lancée")

        while not self.timer.get_fin_match():

            notes = {}

            #initialisation de la recherche de chemin pour le calcul de temps
            self.rechercheChemin.retirer_obstacles_dynamiques()
            self.rechercheChemin.charge_obstacles()
            self.rechercheChemin.prepare_environnement_pour_a_star()

            # Notation des scripts
            for script in self.scripts:
                for version in self.scripts[script].versions():
                    notes[(script,version)] = self._noter_script(script, version)
            self.log.debug("Notes des scripts: " + str(notes))

            # S'il n'y a plus de script à exécuter (ce qui ne devrait jamais arriver), on interrompt la stratégie
            if notes == {}:
                self.log.critical("Plus de scripts à exécuter!")
                break

            # Choix du script avec la meilleure note
            (script_a_faire, version_a_faire) = max(notes, key=notes.get)
            self.log.debug("Stratégie ordonne: ({0}, version n°{1})".format(script_a_faire, version_a_faire))

            # Lancement du script si le match n'est pas terminé
            if not self.timer.get_fin_match():
                
                try:
                    # Tentative d'execution du script
                    self.scripts[script_a_faire].agit(version_a_faire)
                    
                except robot.ExceptionMouvementImpossible:
                    
                    # Enregistrement de l'échec du script
                    if (script_a_faire, version_a_faire) in self.echecs:
                        self.echecs[(script_a_faire, version_a_faire)] += 1
                    else:
                        self.echecs[(script_a_faire, version_a_faire)] = 1
                        
                    self.log.warning('Abandon du script "{0}"'.format(script_a_faire))
                    
                except Exception as e:
                    self.log.warning('Abandon du script "{0}", erreur: {1}'.format(e))

        self.log.debug("Arrêt de la stratégie")

    def _noter_script(self, script, version):
        """
        Note un script (en fonction du nombre de points qu'il peut rapporter, de la position de l'ennemi et de sa durée)
        """
        try:
            duree_script = self.scripts[script].calcule(version)
        except Exception:
            return 0

        # Erreur dans la durée script, script ignoré
        if duree_script <= 0:
            self.log.critical("{0} a un temps d'exécution négatif ou nul!".format((script,version)))
            return 0

        #pour prendre les verres, on ajoute à durée script le temps de déposer les verres
#        if script == "ScriptRecupererVerres" and duree_script + deposer_verre.calcule() > (self.config["temps_match"] - time() + self.timer.get_date_debut()):
#            self.log.warning("Plus le temps de prendre des verres, on n'aurait pas le temps de les déposer.")
#            return 0

        # Si on n'a pas le temps de faire le script avant la fin du match
        if not duree_script < (self.config["temps_match"] - time() + self.timer.get_date_debut()):
            self.log.warning("Plus le temps d'exécuter " + script)
            return 0

        distance_ennemi = self._distance_ennemi(self.scripts[script].point_entree(version))
        score = self.scripts[script].score()
        poids = self.scripts[script].poids()
        
        # Echecs précédents sur le même script
        if (script, version) in self.echecs:
            note_echecs = -self.echecs[(script, version)]
        else:
            note_echecs = 0

        note = [
            # Densité de points
            1*score/duree_script,

            # On évite l'ennemi s'il est proche de l'objectif
            distance_ennemi/400,
            
            # Echecs précédents
            note_echecs
        ]

        return sum(note)

    def _distance_ennemi(self, point_entree):
        """
        Calcule la distance avec les ennemis
        On prend la distance euclidienne, à vol d'oiseau.
        Attention, on prend le min: cette valeur est sensible aux mesures aberrantes
        """

        if self.table.obstacles() == []:
            return 0
            
        return min([point_entree.distance(obstacle.position) for obstacle in self.table.obstacles()])

