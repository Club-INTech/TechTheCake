from src.container import *
import unittest

# Injection du container à la classe de test
ContainerTest.container = Container(env="test")

# Lancement des tests
unittest.main()
