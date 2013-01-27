#module d'injection de dépendances
from src.container import *
container = Container()

#module de la stratégie
strategie = container.get_service("strategie")

strategie.robot.recaler()