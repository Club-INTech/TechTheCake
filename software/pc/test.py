import src.container
import tests.tests
import unittest
import sys

# Injection du container
tests.tests.ContainerTest.container = src.container.Container(env="test")

# Création de la suite de test
if len(sys.argv) > 1:
    suite = unittest.TestLoader().loadTestsFromNames(sys.argv[1:])
else:
    suite = unittest.TestLoader().discover('tests', pattern='*.py', top_level_dir='.')

unittest.TextTestRunner(verbosity=2).run(suite)
