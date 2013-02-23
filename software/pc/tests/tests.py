import unittest

class ContainerTest(unittest.TestCase):
    
    # Container statique injecté depuis le lanceur
    container = None
    
    def get_service(self, service):
        """
        Accéder à un service depuis les tests
        """
        return ContainerTest.container.get_service(service)
        
    def tearDown(self):
        self.container.reset()
