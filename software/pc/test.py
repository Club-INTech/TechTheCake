#module d'injection de dépendances
from src.container import *

container = Container()

Log = container.get_service("log")

Log.debug("Coucou les schtroumpfs")

Log.flush()