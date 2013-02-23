import tests.tests

class TestTable(tests.tests.ContainerTest):
    
    def setUp(self):
        self.table = self.get_service("table")
        
    def test_point_entree_cadeau(self):
        cadeaux = self.table.cadeaux
        self.table.cadeau_recupere(cadeaux[2])
        self.assertEqual(self.table.points_entree_cadeaux, [0, 3])
        self.table.cadeau_recupere(cadeaux[3])
        self.assertEqual(self.table.points_entree_cadeaux, [0, 1])
        self.table.cadeau_recupere(cadeaux[1])
        self.assertEqual(self.table.points_entree_cadeaux, [0, 0])
        self.table.cadeau_recupere(cadeaux[0])
        self.assertEqual(self.table.points_entree_cadeaux, [])
        
    def test_point_entree_bougie(self):
        bougies = self.table.bougies
        self.table.bougie_recupere(bougies[2])
        self.assertEqual(self.table.points_entree_bougies, [3, 17])
        self.table.bougie_recupere(bougies[18])
        self.assertEqual(self.table.points_entree_bougies, [3, 17])
        self.table.bougie_recupere(bougies[17])
        self.assertEqual(self.table.points_entree_bougies, [3, 16])
        self.table.bougie_recupere(bougies[13])
        self.table.bougie_recupere(bougies[14])
        self.table.bougie_recupere(bougies[15])
        self.assertEqual(self.table.points_entree_bougies, [3, 16])
        self.table.bougie_recupere(bougies[16])
        self.assertEqual(self.table.points_entree_bougies, [3, 12])
