#module d'injection de dépendances
from src.container import *

container = Container()

from time import sleep
serie = container.get_service("serie")
    
# Do what the fuck you want
serie.communiquer("cadeaux",["g",100],0)
input()
serie.communiquer("cadeaux",["g",0],0)
input()
serie.communiquer("cadeaux",["g",100],0)
input()
serie.communiquer("cadeaux",["g",0],0)
input()
serie.communiquer("cadeaux",["g",100],0)
input()
serie.communiquer("cadeaux",["g",0],0)
input()
serie.communiquer("cadeaux",["g",100],0)
input()
serie.communiquer("cadeaux",["g",0],0)
input()



