import tests.tests
import time

class TestThreadLaser(tests.tests.ContainerTest):
    
    def test_collision_verre(self):
        simulateur = self.get_service("simulateur")
        table = self.get_service("table")
        simulateur.scriptEnemyPosition(0, {"list":[{"float":[600,1050]}]})
        time.sleep(2)
        self.assertFalse(table.etat_verre(table.verres[0]))
        self.assertTrue(table.etat_verre(table.verres[6]))
