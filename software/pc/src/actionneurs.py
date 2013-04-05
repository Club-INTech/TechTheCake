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
        self.serie.communiquer("capteurs_actionneurs",["cadeau",140],0)
        self.actionneur_cadeaux_actif = True
    
    def fermer_cadeau(self) :
        self.serie.communiquer("capteurs_actionneurs",["cadeau",60],0)
        self.actionneur_cadeaux_actif = False

    def gonfler_ballon(self) :
        self.serie.communiquer("capteurs_actionneurs",["dist_on"], 0)
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
            self.serie.communiquer("capteurs_actionneurs",["haut",160],0)
        else:
            self.log.debug("Enfonce une bougie avec l'actionneur du bas")
            self.serie.communiquer("capteurs_actionneurs",["bas",180],0)
        self.actionneur_bougies_actif = True

    def rentrer_bras_bougie(self) : 
        self.log.debug("Rentre les 2 actionneurs pour bougies")
        self.serie.communiquer("capteurs_actionneurs",["haut",240],0)
        self.serie.communiquer("capteurs_actionneurs",["bas",240],0)
        self.actionneur_bougies_actif = False

    def ascenseur_aller_en_haut(self):
        self.serie.communiquer("ascenseur", "haut", 0)

    def ascenseur_aller_en_bas(self):
        self.serie.communiquer("ascenseur", "bas", 0)

    def ascenseur_ranger(self):
        self.serie.communiquer("capteurs_actionneurs", ["g",0,180] , 0)

    def ascenseur_serrer(self):
        self.serie.communiquer("capteurs_actionneurs", ["g",0,160] , 0)

    def ascenseur_deserrer(self):
        self.serie.communiquer("capteurs_actionneurs", ["g",0,100] , 0)

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
