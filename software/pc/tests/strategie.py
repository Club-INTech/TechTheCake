import tests.tests
from time import sleep

class TestStrategie(tests.tests.ContainerTest):
    
    def test_noter_script(self):
        #les robots ennemis ne doivent pas avoir été instanciés par le simulateur
        scripts = self.get_service("scripts")
        robot = self.get_service("robot")
        table = self.get_service("table")
        strategie = self.get_service("strategie")
        scripts["ScriptCadeaux"].versions()

        note_cadeau_droit = strategie._noter_script("ScriptCadeaux", 0)
        note_cadeau_gauche = strategie._noter_script("ScriptCadeaux", 1)
        self.assertTrue(note_cadeau_droit > note_cadeau_gauche)

        robot.avancer(1000)

        note_cadeau_droit = strategie._noter_script("ScriptCadeaux", 0)
        note_cadeau_gauche = strategie._noter_script("ScriptCadeaux", 1)
        self.assertTrue(note_cadeau_droit > note_cadeau_gauche)

        robot.avancer(500)

        note_cadeau_droit = strategie._noter_script("ScriptCadeaux", 0)
        note_cadeau_gauche = strategie._noter_script("ScriptCadeaux", 1)
        self.assertTrue(note_cadeau_droit < note_cadeau_gauche)
        
        simulateur = self.get_service("simulateur")
        simulateur.addEnemy(0, 80)
        simulateur.scriptEnemyPosition(0, {"list":[{"float":[robot.x-500,robot.y]}]})
        simulateur.startEnemyScript(0)
        
        # Afin que la balise se cale effectivement sur l'ennemi
        sleep(10)

        note_cadeau_droit = strategie._noter_script("ScriptCadeaux", 0)
        note_cadeau_gauche = strategie._noter_script("ScriptCadeaux", 1)
        self.assertTrue(note_cadeau_droit > note_cadeau_gauche)

    def test_executer(self):
        table = self.get_service("table")
        scripts_cadeaux = self.get_service("scripts")["ScriptCadeaux"]
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        scripts_cadeaux.agit(0)
        self.assertEqual(table.cadeaux_restants(), [])
        
