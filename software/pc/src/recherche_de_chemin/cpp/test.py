import os,sys,time

#retrouve le chemin de la racine "software/pc"
directory = os.path.dirname(os.path.abspath(__file__))
racine = "software/pc"
chemin = directory[:directory.index(racine)]+racine
#répertoires d'importation
sys.path.insert(0, os.path.join(chemin, "src/"))

import recherche_chemin
from outils_maths.point import Point

def visilibity_polygon_conversion(path):
    polygon = []
    for i in range(path.size()):
        point = path.get_Point(i)
        polygon.append(Point(point.x(), point.y()))
    return polygon

w = recherche_chemin.VisilibityWrapper(600, 400)

w.epsilon_vis(0.001)
w.tolerance_cv(0)

w.add_rectangle(10, 10, 100, 10, 100, 50, 10, 50)
w.add_rectangle(50, 50, 200, 50, 250, 200, 50, 150)
#w.add_circle(100,100,100)
w.add_circle(230,250,100)
w.add_circle(550,350,100)

#~ w.reset_environment()

t = time.clock()

if w.build_environment() != w.RETURN_OK:
    print("problème avec l'environnement visilibity")
    quit()

print("graphe de visibilité: ", time.clock() - t)
t = time.clock()

for i in range(15):
    path = w.path(5, 5, 100, 200)

print(visilibity_polygon_conversion(path))

print("15x recherche de chemin: ", time.clock() - t)
