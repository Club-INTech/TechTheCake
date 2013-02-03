#module d'injection de dépendances
from src.container import *
container = Container()

#module de la stratégie
strategie = container.get_service("strategie")

#initialisation des coordonnées du robot
strategie.robot.x = 1170#à 33 cm du bord droit : avant du robot sur la ligne rouge/jaune
strategie.robot.y = 270#gauche du robot sur ligne blanc/rouge
strategie.robot.orientation = pi

#on effectue l'arc de cercle vers la gauche : argument '1'
strategie.scripts["bougies"].agit(1)


input("appuyer pour le retour")
#on effectue l'arc de cercle vers la gauche : argument '-1'
strategie.scripts["bougies"].agit(-1)