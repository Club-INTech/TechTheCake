from time import sleep

class Actionneurs :

    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log
        
        #état des actionneurs
        self.actionneur_cadeaux_actif = False
        self.actionneur_bougies_actif = False

    def ouvrir_cadeau(self) :
        self.serie.communiquer("capteurs_actionneurs",["cadeau",110],0)
        self.actionneur_cadeaux_actif = True
            
    def replier_cadeau(self) :
        self.serie.communiquer("capteurs_actionneurs",["cadeau",140],0)
        self.actionneur_cadeaux_actif = True
    
    def fermer_cadeau(self) :
        self.serie.communiquer("capteurs_actionneurs",["cadeau",75],0)
        self.actionneur_cadeaux_actif = False
        
    def replier_cadeau(self) :
        self.serie.communiquer("capteurs_actionneurs",["cadeau",60],0)
        self.actionneur_cadeaux_actif = False

    def gonfler_ballon(self) :
        self.serie.communiquer("capteurs_actionneurs",["dist",self.config["delai_distributeur"]], 0)
        self.log.debug("Gonflage du ballon")
        
    def initialiser_bras_bougie(self, enHaut) : 
        if enHaut:
            self.log.debug("Relève l'actionneur bougie du haut")
            self.serie.communiquer("capteurs_actionneurs",["haut",140],0) # Attention, il ne faut pas les monter trop haut sinon on dépasse la hauteur réglementaire
        else:
            self.log.debug("Relève l'actionneur bougie du bas")
            self.serie.communiquer("capteurs_actionneurs",["bas",150],0)
        self.actionneur_bougies_actif = True

    def enfoncer_bougie(self, enHaut) :
        if enHaut:
            self.log.debug("Enfonce une bougie avec l'actionneur du haut")
            self.serie.communiquer("capteurs_actionneurs",["haut",170],0)
        else:
            self.log.debug("Enfonce une bougie avec l'actionneur du bas")
            self.serie.communiquer("capteurs_actionneurs",["bas",180],0)
        self.actionneur_bougies_actif = True

    def rentrer_bras_bougie(self) : 
        self.log.debug("Rentre les 2 actionneurs pour bougies")
        self.serie.communiquer("capteurs_actionneurs",["haut",240],0)
        self.serie.communiquer("capteurs_actionneurs",["bas",240],0)
        self.actionneur_bougies_actif = False

    def ascenseur_aller_en_haut(self, avant):
        if avant:
            self.log.debug("ascenseur avant levé")
            self.serie.communiquer("ascenseur",["ascenseur_avant","haut"],0)
        else:
            self.log.debug("ascenseur arrière levé")
            self.serie.communiquer("ascenseur",["ascenseur_arriere","haut"],0)
 
    def ascenseur_aller_en_bas(self, avant):
        if avant:
            self.log.debug("ascenseur avant baissé")
            self.serie.communiquer("ascenseur",["ascenseur_avant","bas"],0)
        else:
            self.log.debug("ascenseur arrière baissé")
            self.serie.communiquer("ascenseur",["ascenseur_arriere","bas"],0)

    def ascenseur_ranger(self, avant):
        if avant:
            self.log.debug("ascenseur avant rangé")
            self.serie.communiquer("ascenseur",["ascenseur_avant","g",0,180],0)
        else:
            self.log.debug("ascenseur arrière rangé")
            self.serie.communiquer("ascenseur",["ascenseur_arriere","g",0,180],0)

    def ascenseur_serrer(self, avant):
        if avant:
            self.log.debug("ascenseur avant serré")
            self.serie.communiquer("capteurs_actionneurs",["asc_av",130],0)
        else:
            self.log.debug("ascenseur arrière serré")
            self.serie.communiquer("capteurs_actionneurs",["asc_arr",130],0)

    def ascenseur_deserrer(self, avant):
        if avant:
            self.log.debug("ascenseur avant déserré")
            self.serie.communiquer("capteurs_actionneurs",["asc_av",95],0)
        else:
            self.log.debug("ascenseur arrière déserré")
            self.serie.communiquer("capteurs_actionneurs",["asc_arr",95],0)

    def ascenseur_modifier_constantes(self, valeur):
        """
        Donner le nombre de verres dans l'ascenseur
        0, 1, 2, 3 ou 4
        """

        self.log.debug("Modifier constantes ascenseur pour " + str(valeur) + "verres")
        
        kp = [0.1 ,0 ,0 ,0.01 ,0.01 ]
        kd = [0.001 ,0 ,0 ,0.001 ,0.0001 ]
        ki = [0 ,0 ,0 ,0.0001 ,0 ]
        pwm = [150 ,0 ,0 ,200 ,255 ]

        envoi = ["changerConstantes"]
        envoi.append(int(pwm[valeur]))
        envoi.append(float(kp[valeur]))
        envoi.append(float(kd[valeur]))
        envoi.append(float(ki[valeur]))
        self.serie.communiquer("ascenseur", envoi, 0)
