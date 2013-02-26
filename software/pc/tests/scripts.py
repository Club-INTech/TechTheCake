import tests.tests
from time import sleep

class TestScriptCadeaux(tests.tests.ContainerTest):
    
    def test_point_entree(self):
        table = self.get_service("table")
        scripts_cadeaux = self.get_service("scripts")["ScriptCadeaux"]

        # Cas où tous les cadeaux sont sur la table
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[3]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où le cadeau extrême gauche a été retiré
        table.cadeau_recupere(table.cadeaux[3])
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[2]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où le cadeau extrême gauche a été retiré
        table.cadeau_recupere(table.cadeaux[2])
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[1]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où il n'y a plus qu'un seul cadeau
        table.cadeau_recupere(table.cadeaux[1])
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où il n'y a plus de cadeaux
        table.cadeau_recupere(table.cadeaux[0])
        self.assertEqual(scripts_cadeaux.versions(), [])

    def test_executer(self):
        table = self.get_service("table")
        scripts_cadeaux = self.get_service("scripts")["ScriptCadeaux"]
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        scripts_cadeaux.agit(0)
        self.assertEqual(table.cadeaux_restants(), [])
        

class TestScriptRecupererVerresZoneRouge(tests.tests.ContainerTest):
    
    def test_point_entree(self):
        table = self.get_service("table")
        robot = self.get_service("robot")
        scripts_verres = self.get_service("scripts")["ScriptRecupererVerresZoneRouge"]

        self.assertEqual(scripts_verres.versions(), [0, 1])
        self.assertEqual(scripts_verres.info_versions[0]["point_entree"], table.verres[0]["position"])
        self.assertEqual(scripts_verres.info_versions[1]["point_entree"], table.verres[5]["position"])

        table.verre_recupere(table.verres[5])
        self.assertEqual(scripts_verres.versions(), [0, 1])
        self.assertEqual(scripts_verres.info_versions[0]["point_entree"], table.verres[0]["position"])
        self.assertEqual(scripts_verres.info_versions[1]["point_entree"], table.verres[4]["position"])

        table.verre_recupere(table.verres[4])
        table.verre_recupere(table.verres[3])
        table.verre_recupere(table.verres[2])
        table.verre_recupere(table.verres[1])
        self.assertEqual(scripts_verres.versions(), [0])
        self.assertEqual(scripts_verres.info_versions[0]["point_entree"], table.verres[0]["position"])

        table.verre_recupere(table.verres[0])
        self.assertEqual(scripts_verres.versions(), [])

    def test_score(self):
        table = self.get_service("table")
        robot = self.get_service("robot")
        scripts_verres = self.get_service("scripts")["ScriptRecupererVerresZoneRouge"]

        # On prends les six verres (2 et 4)
        robot.nb_verres_avant = 0
        robot.nb_verres_arriere = 0
        self.assertEqual(scripts_verres.score(), 52)

        # Ascenseur avant plein
        robot.nb_verres_avant = 4
        robot.nb_verres_arriere = 0
        self.assertEqual(scripts_verres.score(), 40)

        # Ascenseur arrière plein
        robot.nb_verres_avant = 0
        robot.nb_verres_arriere = 4
        self.assertEqual(scripts_verres.score(), 40)

        # On ne peut prendre que trois verres
        robot.nb_verres_avant = 3
        robot.nb_verres_arriere = 2
        self.assertEqual(scripts_verres.score(), 44)

# Tests pas encore fonctionnels!
class TestScriptBougies(tests.tests.ContainerTest):
    
    def test_point_entree(self):
        table = self.get_service("table")
        config = self.get_service("config")
        scripts_bougies = self.get_service("scripts")["ScriptBougies"]

        # Le temps que le thread des bougies nous donne leur couleur
        sleep(5)

        # Cas où aucune bougie n'a été soufflée
        self.assertEqual(scripts_bougies.versions(), [0, 1])
        self.assertEqual(scripts_bougies.info_versions[0]["angle_entree"], table.bougies[2]["position"] - 20 / float(500 + config["distance_au_gateau"]))
        self.assertEqual(scripts_bougies.info_versions[1]["angle_entree"], table.bougies[16]["position"] - 20 / float(500 + config["distance_au_gateau"]))

        # Cas où le cadeau extrême gauche a été retiré
        table.cadeau_recupere(table.cadeaux[3])
        self.assertEqual(scripts_bougies.versions(), [0, 1])
        self.assertEqual(scripts_bougies.info_versions[0]["angle_entree"], table.bougies[2]["position"] - 20 / float(500 + config["distance_au_gateau"]))
        self.assertEqual(scripts_bougies.info_versions[1]["angle_entree"], table.bougies[17]["position"] - 20 / float(500 + config["distance_au_gateau"]))

        # Cas où le cadeau extrême gauche a été retiré
        table.cadeau_recupere(table.cadeaux[2])
        self.assertEqual(scripts_bougies.versions(), [0, 1])
        self.assertEqual(scripts_bougies.info_versions[0]["angle_entree"], table.bougies[2]["position"] - 20 / float(500 + config["distance_au_gateau"]))
        self.assertEqual(scripts_bougies.info_versions[1]["angle_entree"], table.bougies[17]["position"] - 20 / float(500 + config["distance_au_gateau"]))

        # Cas où il n'y a plus qu'un seul cadeau
        table.cadeau_recupere(table.cadeaux[1])
        self.assertEqual(scripts_bougies.versions(), [0, 1])
        self.assertEqual(scripts_bougies.info_versions[0]["angle_entree"], table.bougies[2]["position"] - 20 / float(500 + config["distance_au_gateau"]))
        self.assertEqual(scripts_bougies.info_versions[1]["angle_entree"], table.bougies[17]["position"] - 20 / float(500 + config["distance_au_gateau"]))

        # Cas où il n'y a plus de cadeaux
        table.bougies_recupere(table.cadeaux[0])
        self.assertEqual(scripts_bougies.versions(), [])

