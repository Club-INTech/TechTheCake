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
            self.serie.communiquer("capteurs_actionneurs",["cadeau",80],0)
            self.actionneur_cadeaux_actif = True
        elif angle == "haut":
            self.serie.communiquer("capteurs_actionneurs",["cadeau",120],0)
            self.actionneur_cadeaux_actif = True

    def gonfler_ballon(self, pwm = False) :
        if(pwm) :
            for i in range(self.config["ballon_iteration"]) :
                self.serie.communiquer("capteurs_actionneurs",["dist",self.config["ballon_delai_pwm"]], 0)
                sleep(self.config["ballon_sleep"])
        else :
            self.serie.communiquer("capteurs_actionneurs",["dist",self.config["ballon_delai_unique"]], 0)
        self.log.debug("Gonflage du ballon")

    def actionneurs_bougie(self, en_haut, angle):
        if en_haut:
            if angle == "bas":
                self.serie.communiquer("capteurs_actionneurs",["haut",247],0)
                self.actionneur_bougies_actif = False
            elif angle == "moyen":
                self.serie.communiquer("capteurs_actionneurs",["haut",180],0)
                self.actionneur_bougies_actif = True
            elif angle == "haut":
                self.serie.communiquer("capteurs_actionneurs",["haut",150],0)
                self.actionneur_bougies_actif = True
        else:
            if angle == "bas":
                self.serie.communiquer("capteurs_actionneurs",["bas",250],0)
                self.actionneur_bougies_actif = False
            elif angle == "moyen":
                self.serie.communiquer("capteurs_actionneurs",["bas",180],0)
                self.actionneur_bougies_actif = True
            elif angle == "haut":
                self.serie.communiquer("capteurs_actionneurs",["bas",150],0)
                self.actionneur_bougies_actif = True

    def altitude_ascenseur(self, avant, hauteur):
        if avant:
            self.serie.communiquer("ascenseur",["asc_av",hauteur],0)
        else:
            self.serie.communiquer("ascenseur",["asc_ar",hauteur],0)

    def actionneurs_ascenseur(self, avant, position):
        if position == "ferme_completement":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",175],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",175],0)
        elif position == "ferme":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",155],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",148],0)
        elif position == "petit ouvert":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",140],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",140],0)
        elif position == "ouvert":
            if avant:
                self.serie.communiquer("capteurs_actionneurs",["asc_av",123],0)
            else:
                self.serie.communiquer("capteurs_actionneurs",["asc_arr",123],0)


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
