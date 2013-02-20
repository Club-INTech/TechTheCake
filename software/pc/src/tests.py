import unittest

class ContainerTest(unittest.TestCase):
    
    # Container statique injecté depuis le lanceur
    container = None
    
    def get_service(service):
        """
        Accéder à un service depuis les tests
        """
        return ContainerTest.container.get_service(service)
    
