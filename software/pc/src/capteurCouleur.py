import abc

class CapteurCouleur(metaclass = abc.ABCMeta):

	@abc.abstractmethod
	def lire_couleur(self):
		pass


class CapteurCouleurSerie( CapteurCouleur ):

	def __init__(self,serie,config,log):
		self.serie = serie
		self.config = config
		self.log = log

	def lire_couleur(self):
		return self.serie.communiquer("capteur",["couleur"],1)
		

class CapteurCouleurSimulateur( CapteurCouleur ):

	def __init__(self,serie,config,log):
		self.serie = serie
		self.config = config
		self.log = log
	
	def lire_couleur(self):
		pass

