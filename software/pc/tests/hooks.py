import tests.tests
from src.outils_maths.point import Point
        
class TestHook(tests.tests.ContainerTest):
    
    def test_callbacks(self):
        
        # Création d'une fonction à appeler
        return_1 = False
        def fonction_test_1():
            nonlocal return_1
            return_1 = True
            
        # Création d'une fonction à appeler avec arguments
        return_2 = False
        def fonction_test_2(arg1, arg2):
            if arg1 == "test":
                nonlocal return_2
                return_2 = True
            
        # Création d'un hook
        self.factory = self.get_service("hookGenerator")
        hook = self.factory.hook_position(Point(0, 0))
        
        # Attachement d'un premier callback
        hook += self.factory.callback(fonction_test_1)
        
        # Attachement d'un second callback avec arguments
        hook += self.factory.callback(fonction_test_2, ("test", None))
        
        # Déclenchement du hook
        hook.declencher()
        
        # Vérification que les 2 callbacks ont été appelés
        self.assertTrue(return_1)
        self.assertTrue(return_2)
        
    def test_callbacks_unique(self):
        
        # Création d'une fonction à appeler une seule fois
        return_1 = 0
        def fonction_test_1():
            nonlocal return_1
            return_1 += 1
            
        # Création d'une fonction à appeler plusieurs fois
        return_2 = 0
        def fonction_test_2():
            nonlocal return_2
            return_2 += 1
            
        # Création d'un hook
        self.factory = self.get_service("hookGenerator")
        hook = self.factory.hook_position(Point(0, 0))
        
        # Attachement d'un premier callback
        hook += self.factory.callback(fonction_test_1, unique=True)
        
        # Attachement d'un second callback non unique
        hook += self.factory.callback(fonction_test_2, unique=False)
        
        # Déclenchement du hook
        hook.declencher()
        hook.declencher()
        hook.declencher()
        
        # Vérification que les 2 callbacks ont été appelés
        self.assertEqual(return_1, 1)
        self.assertTrue(return_2, 3)
        
