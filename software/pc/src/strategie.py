from time import sleep,time
from scripts import *
import robot
from outils_maths.point import Point
import recherche_de_chemin.rechercheChemin as libRechercheChemin

class Strategie:
    """
    Classe gérant l'intelligence artificielle.
    Son rôle est de noter différents scripts (selon leur durée, la distance d'un ennemi, ...) et de choisir le plus avantageux. 
    C'est également cette classe qui fait les appels d'ajout d'obstacle à la recherche de chemin.
    """
    def __init__(self, scripts, rechercheChemin, table, timer, config, log, robot):

        self.scripts = scripts
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log
        self.robot = robot
        
        self.echecs = {}

    def boucle_strategie(self):
        """
        Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
        """

        while not self.timer.match_demarre:
            sleep(.5)

        self.log.debug("Stratégie lancée")
        # Avec la balise laser, récupérer la position des ennemis. Sur la ou les cases occupées seront probablement les verres
        self.robot.avancer(200, retenter_si_blocage = False, sans_lever_exception = True)

        # On ne le fait que maintenant car la config peut changer avant le début du match
        if self.config["ennemi_fait_toutes_bougies"]:
            self.log.warning("Comme l'ennemi fait toutes les bougies, on ne les fera pas.")
            del self.scripts["ScriptBougies"]
    
        while not self.timer.get_fin_match():

            notes = {}

            #initialisation de la recherche de chemin pour le calcul de temps
            self.rechercheChemin.retirer_obstacles_dynamiques()
            self.rechercheChemin.charge_obstacles(avec_verres_entrees=False)
            self.rechercheChemin.prepare_environnement_pour_a_star()
            
            # Notation des scripts
            for script in self.scripts:
                for version in self.scripts[script].versions():
                    notes[(script,version)] = self._noter_script(script, version)
            self.log.debug("Notes des scripts: " + str(notes))

            # S'il n'y a plus de script à exécuter (ce qui ne devrait jamais arriver), on interrompt la stratégie
            if notes == {}:
                self.log.critical("Plus de scripts à exécuter! Temps restant: "+str(self.config["temps_match"] - time() + self.timer.get_date_debut()))
                break

            # Choix du script avec la meilleure note
            (script_a_faire, version_a_faire) = max(notes, key=notes.get)
            self.log.debug("Stratégie ordonne: ({0}, version n°{1}, entrée en {2})".format(script_a_faire, version_a_faire, self.scripts[script_a_faire].point_entree(version_a_faire)))
            
            #ajout d'obstacles pour les verres d'entrées, sauf si on execute un script de récupération des verres
            if not isinstance(self.scripts[script_a_faire], ScriptRecupererVerres):
                for verre in self.table.verres_entrees():
                    self.rechercheChemin.ajoute_obstacle_cercle(verre["position"], self.config["rayon_verre"])

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
                        
                    self.log.warning('Abandon du script "{0}". Echec enregistré'.format(script_a_faire))
                    
                except Exception as e:
                    self.log.warning('Abandon du script "{0}", erreur: {1}'.format(script_a_faire, e))

            else:
                self.log.warning("Ordre annulé: fin du match.")

        self.log.debug("Arrêt de la stratégie")

    def _noter_script(self, script, version):
        """
        Note un script (en fonction du nombre de points qu'il peut rapporter, de la position de l'ennemi et de sa durée)
        """
        try:
            duree_script = self.scripts[script].calcule(version)
            
        #chemin impossible
        except libRechercheChemin.ExceptionAucunChemin:
            return -1000
        except libRechercheChemin.ExceptionArriveeDansObstacle:
            return -1000
        except libRechercheChemin.ExceptionArriveeHorsTable:
            return -1000
            
        # Erreur dans la durée script, script ignoré
        if duree_script <= 0:
            self.log.critical("{0} a un temps d'exécution négatif ou nul!".format((script,version)))
            return -1000

        #pour prendre les verres, on ajoute à durée script le temps de déposer les verres
#        if script == "ScriptRecupererVerres" and duree_script + deposer_verre.calcule() > (self.config["temps_match"] - time() + self.timer.get_date_debut()):
#            self.log.warning("Plus le temps de prendre des verres, on n'aurait pas le temps de les déposer.")
#            return 0

        # Si on n'a pas le temps de faire le script avant la fin du match
        if not duree_script < (self.config["temps_match"] - time() + self.timer.get_date_debut()):
            self.log.warning("Plus le temps d'exécuter " + script)
            self.log.warning("Son temps: " + str(duree_script)+". Temps restant: " + str(self.config["temps_match"] - time() + self.timer.get_date_debut()))
            malus = -10
        else:
            malus = 0

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
            5*score/duree_script,

            # On évite l'ennemi s'il est proche de l'objectif (gaussienne)
            -10*math.exp(-(distance_ennemi**4)/(5*10**11)),
            
            # Echecs précédents
            5*note_echecs,
    
            # Fonction du temps
            poids,

            # Les scripts qu'on aurait pas le temps de finir ont un malus de points
            malus
        ]
#        self.log.critical("Détail note "+str(script)+" en "+str(self.scripts[script].point_entree(version))+": "+str(note))
#        self.log.critical("Score: "+str(score)+", durée: "+str(duree_script))

        
        return sum(note)

    def _distance_ennemi(self, point_entree):
        """
        Calcule la distance avec les ennemis
        On prend la distance euclidienne, à vol d'oiseau.
        Attention, on prend le min: cette valeur est sensible aux mesures aberrantes
        """
        duree_du_trajet = 2
        
        #obstacles avec vitesse
        positions = [point_entree.distance(obstacle.position)+duree_du_trajet*obstacle.vitesse.norme() for obstacle in self.table.obstacles() if hasattr(obstacle, "vitesse") and obstacle.vitesse is not None]
        #obstacles sans vitesse
        positions += [point_entree.distance(obstacle.position) for obstacle in self.table.obstacles() if not hasattr(obstacle, "vitesse")]

        # S'il n'y a aucun ennemi, on considère qu'il est à l'infini
        if positions == []:
            return 5000
        return min(positions)
