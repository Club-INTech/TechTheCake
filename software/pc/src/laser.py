import abc

class Laser(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def allumer(self):
        pass
        
    @abc.abstractmethod
    def eteindre(self):
        pass
        
    @abc.abstractmethod
    def ping_balise(self):
        pass
        
    @abc.abstractmethod
    def frequence_moteur(self):
        pass
        
    @abc.abstractmethod
    def valeur(self, id_balise):
        pass

        
class LaserSerie(Laser):
    
    def __init__(self, serie, config, log):
        self.serie = serie
        self.config = config
        self.log = log
    
    def allumer(self):
        self.serie.communiquer("laser", ["motor_on"], 0)
        self.serie.communiquer("laser", ["laser_on"], 0)
        
    def eteindre(self):
        self.serie.communiquer("laser", ["laser_off"], 0)
        self.serie.communiquer("laser", ["motor_off"], 0)
        
    def ping_balise(self):
        pass
        
    def frequence_moteur(self):
        reponse = self.serie.communiquer("laser", ["freq"], 1)
        return reponse[0]
        
    def valeur(self, id_balise):
        reponse = self.serie.communiquer("laser", ["valeur", id_balise], 1)
        rayon = reponse[0]
        angle = reponse[1]
        pass
    
class LaserSimulateur(Laser):
    
    def __init__(self, simulateur, config, log):
        self.simulateur = simulateur
        self.config = config
        self.log = log
        
    def allumer(self):
        self.simulateur.log("Allumage des lasers")
        
    def eteindre(self):
        self.simulateur.log("Extinction des lasers") 
        
    def ping_balise(self):
        pass
        
    def frequence_moteur(self):
        pass
        
    def valeur(self, id_balise):
        pass
        
        
""""
from serial import Serial
from time import sleep
from suds.client import Client
import math

def write(serie, args):
	return serie.write(bytes(args + "\r","utf-8"))

def read(serie):
	return clean_string(str(serie.readline(),"utf-8"))
	
def clean_string(chaine):
    return chaine.replace("\n","").replace("\r","").replace("\0","")   

def position(r, a):
	delai = float(r)/(20000000./(128.))
	theta = delai * 17.9 * 2 * math.pi
	d = 35. / math.sin(theta / 2.)
	#print("ms = {0} d = {1}".format(1000*delai, d))
	x = 0 - d * math.cos(math.radians(a))
	y = 2000 + d * math.sin(math.radians(a))
	return [x, y]

simulateur = Client("http://localhost:8090/INTechSimulator?wsdl").service

simulateur.reset()
simulateur.setTableDimension(3000,2000)
simulateur.defineCoordinateSystem(1,0,0,-1,1500,2000)

serie = Serial("/dev/ttyUSB0", 9600, timeout=0.1)
     
print("Allumage du moteur et des lasers...")
write(serie, "motor_on")
write(serie, "laser_on")

#sleep(1)

while(1):
	write(serie, "valeurb")
	val = read(serie).split(",")
	try:
		r = int(val[0])
		if r == 0:
			continue
		a = float(val[1]) - 55
		if a < 0: a = a + 360
		pos = position(r,a)
		print("{0};{1};{2};{3}".format(r,a,pos[0],pos[1]))
		simulateur.drawPoint(pos[0],pos[1],'red',False)
	except:
		pass
serie.close()
"""
