import tests.tests

class TestCapteurs(tests.tests.ContainerTest):
    
    def setUp(self):
        pass

    def test_shuffle(self):
        self.assertTrue(True)

    def test_mesurer(self):
        capteurs = self.get_service("capteurs")
        robot = self.get_service("robot")
        simulateur = self.get_service("simulateur")
        simulateur.scriptEnemyPosition(0, {"list":[{"float":[robot.x-500,robot.y]}]})
        simulateur.startEnemyScript(0)
        self.assertTrue(capteurs.mesurer(), 500)
        self.assertTrue(capteurs.mesurer(True), 0)

    def test_mesurer2(self):
        capteurs = self.get_service("capteurs")
        robot = self.get_service("robot")
        robot.avancer(1000)
        simulateur = self.get_service("simulateur")
        simulateur.scriptEnemyPosition(0, {"list":[{"float":[robot.x+500,robot.y]}]})
        simulateur.startEnemyScript(0)
        self.assertTrue(capteurs.mesurer(), 0)
        self.assertTrue(capteurs.mesurer(True), 500)

