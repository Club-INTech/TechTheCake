import tests.tests
import src.table

class TestTable(tests.tests.ContainerTest):
    
    def setUp(self):
        self.table = self.get_service("table")
        
    def test_point_entree_cadeau(self):
        cadeaux = self.table.cadeaux
        self.table.cadeau_recupere(cadeaux[2])
        self.assertEqual(self.table.cadeaux_entrees(), [cadeaux[0], cadeaux[3]])
        self.table.cadeau_recupere(cadeaux[3])
        self.assertEqual(self.table.cadeaux_entrees(), [cadeaux[0], cadeaux[1]])
        self.table.cadeau_recupere(cadeaux[1])
        self.assertEqual(self.table.cadeaux_entrees(), [cadeaux[0], cadeaux[0]])
        self.table.cadeau_recupere(cadeaux[0])
        self.assertEqual(self.table.cadeaux_entrees(), [])
        
    def test_point_entree_bougie(self):
        bougies = self.table.bougies
        self.table.bougie_recupere(bougies[2])
        self.assertEqual(self.table.bougies_entrees(), [bougies[3], bougies[17]])
        self.table.bougie_recupere(bougies[18])
        self.assertEqual(self.table.bougies_entrees(), [bougies[3], bougies[17]])
        self.table.bougie_recupere(bougies[17])
        self.assertEqual(self.table.bougies_entrees(), [bougies[3], bougies[16]])
        self.table.bougie_recupere(bougies[13])
        self.table.bougie_recupere(bougies[14])
        self.table.bougie_recupere(bougies[15])
        self.assertEqual(self.table.bougies_entrees(), [bougies[3], bougies[16]])
        self.table.bougie_recupere(bougies[16])
        self.assertEqual(self.table.bougies_entrees(), [bougies[3], bougies[12]])
        
    def test_point_entree_verre(self):
        verres = self.table.verres
        self.table.verre_recupere(verres[0])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [verres[1], verres[5]])
        self.table.verre_recupere(verres[5])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [verres[1], verres[4]])
        self.table.verre_recupere(verres[2])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [verres[1], verres[4]])
        self.table.verre_recupere(verres[3])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [verres[1], verres[4]])
        self.table.verre_recupere(verres[1])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [verres[4]])
        self.table.verre_recupere(verres[4])
        self.assertEqual(self.table.verres_entrees(src.table.Table.ZONE_VERRE_ROUGE), [])
