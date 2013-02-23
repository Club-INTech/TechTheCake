import tests.tests

class TestScriptCadeaux(tests.tests.ContainerTest):
    
    def setUp(self):
        pass

    def test_shuffle(self):
        self.assertTrue(True)

    def test_point_entree(self):
        table = self.get_service("table")
        scripts_cadeaux = self.get_service("scripts")["ScriptCadeaux"]

        # Cas où tous les cadeaux sont sur la table
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[3]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où un cadeau extrême gauche a été retiré
        table.cadeau_recupere(table.cadeaux[3])
        self.assertEqual(scripts_cadeaux.versions(), [0, 1])
        self.assertEqual(scripts_cadeaux.info_versions[0]["point_entree"], table.cadeaux[0]["position"]+scripts_cadeaux.decalage_droit)
        self.assertEqual(scripts_cadeaux.info_versions[1]["point_entree"], table.cadeaux[2]["position"]+scripts_cadeaux.decalage_gauche)

        # Cas où un cadeau extrême gauche a été retiré
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
        scripts_cadeaux.executer(0)
        self.assertEqual(table.cadeaux_restants(), [])
        
