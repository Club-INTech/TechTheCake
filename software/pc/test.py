import src.container
import tests.tests
import unittest
import sys

"""

LANCEMENT DES TESTS

Lancer tous les tests présents:
$ python3 test.py

Lancer les tests d'un module
$ python3 test.py tests.nom_du_module

Lancer les tests d'une classe de test
$ python3 test.py tests.nom_du_module.nom_de_la_classe

Lancer un seul test
$ python3 test.py tests.nom_du_module.nom_de_la_classe.methode

"""

# Injection du container
tests.tests.ContainerTest.container = src.container.Container(env="test")

# Création de la suite de test
if len(sys.argv) > 1:
    suite = unittest.TestLoader().loadTestsFromNames(sys.argv[1:])
else:
    suite = unittest.TestLoader().discover('tests', pattern='*.py', top_level_dir='.')

unittest.TextTestRunner(verbosity=2).run(suite)
