#module d'injection de dépendances
from src.container import *
container = Container()


#module de la stratégie
from src.strategie import Strategie
strategie = container.get_service("strategie")

strategie.robot.avancer(1000)
strategie.robot.tourner(1.57)
