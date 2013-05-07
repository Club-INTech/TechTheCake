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
    def __init__(self, scripts, rechercheChemin, table, timer, config, log, robot, son):

        self.scripts = scripts
        self.rechercheChemin = rechercheChemin
        self.table = table
        self.timer = timer
        self.config = config
        self.log = log
        self.robot = robot
        self.son = son

        self.echecs = {}

    def boucle_strategie(self):
        """
        Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
        """
        # La première décision est scriptée
        premier_tour = True

        if self.config["couleur"] == "bleu":
            script_a_faire = "ScriptRecupererVerresZoneBleu"
        else:
            script_a_faire = "ScriptRecupererVerresZoneRouge"
        self.scripts[script_a_faire].versions()
        if abs(self.scripts[script_a_faire].point_entree(0).y - self.robot.y) < abs(self.scripts[script_a_faire].point_entree(1).y - self.robot.y):
            version_a_faire = 0
        else:
            version_a_faire = 1
            
        self.log.debug("stratégie en attente du jumper...")

        while not self.timer.match_demarre:
            sleep(.5)
            
        self.son.jouer("debut")
        self.log.debug("stratégie lancée")
        
        # Avec la balise laser, récupérer la position des ennemis. Sur la ou les cases occupées seront probablement les verres.
        # Mettre à jour position_verres_1 et position_verres_2
#        self.scripts["ScriptRenverserVerres"].cases_verres=[1,2]
        try:
            self.robot.set_vitesse_translation("entre_scripts")
            self.robot.set_vitesse_rotation("entre_scripts")
            self.robot.avancer(300, retenter_si_blocage = False, sans_lever_exception = True)
        except:
            pass
        self.robot.actionneurs_ascenseur(True, "ouvert")
        self.robot.actionneurs_ascenseur(False, "ouvert")

        # On ne le fait que maintenant car la config peut changer avant le début du match
        if self.config["ennemi_fait_toutes_bougies"]:
            self.log.warning("Comme l'ennemi fait toutes les bougies, on ne les fera pas.")
            del self.scripts["ScriptBougies"]

        while not self.timer.get_fin_match():

            if not premier_tour:
                notes = {}

                #initialisation de la recherche de chemin pour le calcul de temps
                self.rechercheChemin.retirer_obstacles_dynamiques()
                self.rechercheChemin.charge_obstacles(avec_verres_entrees=False)
                
                try: self.rechercheChemin.prepare_environnement_pour_visilibity()
                except libRechercheChemin.ExceptionEnvironnementMauvais as e:
                    self.log.critical(e)
                    sleep(0.1)
                    continue
                
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
#                script_a_faire = "ScriptBougies"
#                version_a_faire = 0
                self.log.debug("Stratégie ordonne: ({0}, version n°{1}, entrée en {2})".format(script_a_faire, version_a_faire, self.scripts[script_a_faire].point_entree(version_a_faire)))
                
                input()
                """
                #ajout d'obstacles pour les verres d'entrées, sauf si on execute un script de récupération des verres
                if not isinstance(self.scripts[script_a_faire], ScriptRecupererVerres):
                    self.rechercheChemin.retirer_obstacles_dynamiques()
                    self.rechercheChemin.charge_obstacles(avec_verres_entrees=True)
                    
                    try: self.rechercheChemin.prepare_environnement_pour_visilibity()
                    except libRechercheChemin.ExceptionEnvironnementMauvais as e:
                        self.log.critical(e)
                        sleep(0.1)
                        continue
                """
            
            premier_tour = False;

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

            self.robot.deposer_verre_avant = self.robot.nb_verres_avant >= 2 or (self.robot.nb_verres_avant >= 1 and time() - self.timer.get_date_debut() >= self.config["duree_combo"])
            self.robot.deposer_verre_arriere = self.robot.nb_verres_arriere >= 2 or (self.robot.nb_verres_arriere >= 1 and time() - self.timer.get_date_debut() >= self.config["duree_combo"])

            self.log.debug("Peut-on déposer à l'avant? "+str(self.robot.deposer_verre_avant))
            self.log.debug("Peut-on déposer à l'arrière? "+str(self.robot.deposer_verre_arriere))

        self.log.debug("Arrêt de la stratégie")

    def _noter_script(self, script, version):
        """
        Note un script (en fonction du nombre de points qu'il peut rapporter, de la position de l'ennemi et de sa durée)
        """
        try:
            duree_script = self.scripts[script].calcule(version)
            
        #chemin impossible
        except libRechercheChemin.ExceptionAucunChemin:
            self.log.critical("Epic fail de {0}! ExceptionAucunChemin".format((script,version)))
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
            1000 * score/duree_script,

            # On évite l'ennemi s'il est proche de l'objectif (gaussienne)
            -10*math.exp(-(distance_ennemi**4)/(5*10**11)),
            
            # Echecs précédents
            2*note_echecs,
    
            # Fonction du temps
            poids,

            # Les scripts qu'on aurait pas le temps de finir ont un malus de points
            malus
        ]
        self.log.debug("Détail note "+str(script)+" en "+str(self.scripts[script].point_entree(version))+": "+str(note))
#        self.log.debug("Score: "+str(score)+", durée: "+str(duree_script))
        
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
        positions += [point_entree.distance(obstacle.position) for obstacle in self.table.obstacles() if not hasattr(obstacle, "vitesse") or obstacle.vitesse is None]

        # S'il n'y a aucun ennemi, on considère qu'il est à l'infini
        if positions == []:
            return 5000
        return min(positions)
