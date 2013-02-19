from outils_maths.point import Point
from outils_maths.vitesse import Vitesse
from math import cos,sin
from time import sleep
from time import time

def fonction_laser(container):
    """
    Cette fonction sera lancée dans un thread parallèle à la stratégie.
    Les différentes balises sont intérrogées régulièrement, les résultats sont filtrés puis passés au service de table
    """
    
    # importation des services nécessaires
    log = container.get_service("log")
    config = container.get_service("config")
    laser = container.get_service("laser")
    filtrage = container.get_service("filtrage")
    table = container.get_service("table")
    timer = container.get_service("timer")
    simulateur = container.get_service("simulateur")

    log.debug("Lancement du thread des lasers")

    # Attente du démarrage du match et qu'au moins une balise réponde
    while not timer.match_demarre or laser.verifier_balises_connectes() == 0:
        sleep(0.1)
        
    # Liste des balises non prises en compte
    for balise in laser.balises_ignorees():
        log.warning("balise n°" + str(balise["id"]) + " ignorée pendant le match, pas de réponses aux ping")

    # Liste des balises prises en compte
    balises = laser.balises_actives()
    
    while not timer.get_fin_match():
        
        for balise in balises:
            
            # Récupération de la position brute
            p_bruit = laser.position_balise(balise["id"])
            
            # Mise à jour du modèle de filtrage
            filtrage.update(p_bruit[0], p_bruit[1])
            
            # Récupération des valeurs filtrées
            p_filtre = filtrage.position()
            vitesse = filtrage.vitesse()
            
            # Mise à jour de la table
            table.deplacer_robot_adverse(0, Point(int(p_filtre[0]), int(p_filtre[1])), Vitesse(int(vitesse[0]), int(vitesse[1])))
            
            # Affichage des points sur le simulateur
            if config["mode_simulateur"]:
                if config["lasers_afficher_valeurs_brutes"]:
                    simulateur.drawPoint(p_bruit[0], p_bruit[1], "gris")
                if config["lasers_afficher_valeurs_filtre"]:
                    simulateur.drawPoint(int(p_filtre[0]), int(p_filtre[1]), "blue")
        
        sleep(1./config["lasers_frequence"])
        
    log.debug("Arrêt du thread des lasers")

