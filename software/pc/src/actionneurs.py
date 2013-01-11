import abc # classe abstraite


class Actionneurs(metaclass=abc.ABCMeta):

    @abc.abstractmethod # abstraite : rien dedans mais plante si rien après (def de la méthode abstraite)
    def ouvrir_cadeau(self):
        pass
        
    @abc.abstractmethod
    def fermer_cadeau(self):
        pass

class ActionneursSerie(Actionneurs) : #héritage

    def __init__(self,serie,config,log):
        #services utilisés
        self.serie = serie
        self.config = config
        self.log = log

    def ouvrir_cadeau(self) :
        self.serie.communiquer("cadeaux",["g",240],0)
    
    def fermer_cadeau(self) :
        self.serie.communiquer("cadeaux",["g",150],0)
        
    def initialiser_bras_bougie(self) : 
	self.serie.communiquer("couleur",["g",240],0)

    def enfoncer_bougie(self) :
	self.serie.communiquer("couleur",["g",220],0)

    def rentrer_bras_bougie(self) : 
	self.serie.communiquer("couleur",["g",150],0)

class ActionneursSimulateur(Actionneurs) :
     
    def __init__(self,simulateur,config,log):
        #services utilisés
        self.simulateur = simulateur
        self.config = config
        self.log = log    
     
    def ouvrir_cadeau(self) :
        self.log.debug("Ouverture actionneur cadeau")
    
    def fermer_cadeau(self) :
        self.log.debug("Fermeture actionneur cadeau")
