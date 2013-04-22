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

    def actionneur_cadeau(self, angle) :
        if angle == "bas":
            self.serie.communiquer("capteurs_actionneurs",["cadeau",60],0)
            self.actionneur_cadeaux_actif = False
        elif angle == "moyen":
            self.serie.communiquer("capteurs_actionneurs",["cadeau",85],0)
            self.actionneur_cadeaux_actif = True
        elif angle == "haut":
            self.serie.communiquer("capteurs_actionneurs",["cadeau",110],0)
            self.actionneur_cadeaux_actif = True

    def gonfler_ballon(self) :
        self.serie.communiquer("capteurs_actionneurs",["dist",self.config["delai_distributeur"]], 0)
        self.log.debug("Gonflage du ballon")

    def actionneurs_bougie(self, en_haut, angle):
        if en_haut:
            if angle == "bas":
                self.serie.communiquer("capteurs_actionneurs",["haut",240],0)
                self.actionneur_bougies_actif = False
            elif angle == "moyen":
                self.serie.communiquer("capteurs_actionneurs",["haut",180],0)
                self.actionneur_bougies_actif = True
            elif angle == "haut":
                self.serie.communiquer("capteurs_actionneurs",["haut",150],0)
                self.actionneur_bougies_actif = True
        else:
            if angle == "bas":
                self.serie.communiquer("capteurs_actionneurs",["bas",240],0)
                self.actionneur_bougies_actif = False
            elif angle == "moyen":
                self.serie.communiquer("capteurs_actionneurs",["bas",180],0)
                self.actionneur_bougies_actif = True
            elif angle == "haut":
                self.serie.communiquer("capteurs_actionneurs",["bas",150],0)
                self.actionneur_bougies_actif = True

    def altitude_ascenseur(self, avant, hauteur):
        if avant:
            if hauteur == "moyen":
                self.serie.communiquer("ascenseur",["asc_av","consigne",10],0)
            else:
                self.serie.communiquer("ascenseur",["asc_av",hauteur],0)
        else:
            if hauteur == "moyen":
                self.serie.communiquer("ascenseur",["asc_ar","consigne",10],0)
            else:
                self.serie.communiquer("ascenseur",["asc_ar",hauteur],0)

    def actionneurs_ascenseur(self, avant, position):
        if position == "fermé":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",120],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",120],0)
#        elif position == "ouvert":
#            if avant:
#                self.serie.communiquer("capteurs_actionneurs",["asc_av",95],0)
#            else:
#                self.serie.communiquer("capteurs_actionneurs",["asc_arr",95],0)
        elif position == "ouvert":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",85],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",85],0)


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
