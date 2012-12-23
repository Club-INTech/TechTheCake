from serial import Serial
from mutex import Mutex
import os
from time import sleep
        
        
class Peripherique:
    """
    structure décrivant un périphérique série :
    id : ping attendu de la carte (0 pour l'asservissement...)
    baudrate : (9600, 57600...)
    serie : chemin du périphérique (/dev/ttyACM0...)
    """
    def __init__(self,id,baudrate):
        self.id = id
        self.baudrate = baudrate
        
class Serie:
        
    def __init__(self, log):
        
        #instances des dépendances
        self.log = log
        
        #mutex évitant les écritures/lectures simultanées sur la série
        self.mutex = Mutex()
        #dictionnaire des périphériques recherchés
        self.peripheriques = {"asservissement": Peripherique(0,9600),"capteurs_actionneurs" : Peripherique(3,9600), "cadeaux" : Peripherique(6,9600), "ascenseur": Peripherique(2,9600),"pince_verre": Peripherique(8,9600)}
        #attribution initiale des périphériques
        self.attribuer()
        
    def attribuer(self):
        #liste les chemins trouvés dans /dev
        sources = os.popen('ls -1 /dev/ttyUSB* 2> /dev/null').readlines()
        sources.extend(os.popen('ls -1 /dev/ttyACM* 2> /dev/null').readlines())
        
        if not sources:
            print("\nAucun périphérique trouvé. Seconde tentative en sudo...")
            sources = os.popen('sudo ls -1 /dev/ttyUSB* 2> /dev/null').readlines()
            sources.extend(os.popen('ls -1 /dev/ttyACM* 2> /dev/null').readlines())
            
        for k in range(len(sources)):
            sources[k] = sources[k].replace("\n","")
        
        #liste les baudrates des périphériques recherchés
        baudrates = []
        for destinataire in (self.peripheriques):
            if not self.peripheriques[destinataire].baudrate in baudrates:
                baudrates.append(self.peripheriques[destinataire].baudrate)
        
        #recherche les pings présents sur les chemins et baudrates listés
        pings = {}
        for baudrate in baudrates:
            print("liste des pings pour le baudrate "+str(baudrate)+" :")
            for source in sources:
                try:
                    instanceSerie = Serial(source, baudrate, timeout=0.1)
                    
                    #vide le buffer de l'avr
                    instanceSerie.flushInput()
                    #ping
                    instanceSerie.write(bytes("?\r","utf-8"))
                    #évacuation de l'acquittement
                    instanceSerie.readline()
                    #réception de l'id de la carte
                    rep = self.clean_string(str(instanceSerie.readline(),"utf-8"))
                    #fermeture du périphérique
                    instanceSerie.close()
                    #tentative de cast pour extraire un id
                    try:
                        id = int(rep)
                        pings[id]=source
                        print(" * "+str(id)+" sur "+source)
                    except:
                        pass
                except Exception as e:
                    print(e)
                    
        #attribue les instances de série pour les périphériques ayant le bon ping
        for destinataire in (self.peripheriques):
            if self.peripheriques[destinataire].id in pings:
                source = pings[self.peripheriques[destinataire].id]
                self.log.debug(destinataire+" OK sur "+source)
                self.peripheriques[destinataire].chemin = source
                self.peripheriques[destinataire].serie = Serial(source, self.peripheriques[destinataire].baudrate, timeout=0.1)
            else:
                self.log.warning(destinataire+" non trouvé !")
        
    def clean_string(self, chaine):
        #suppressions des caractères spéciaux sur la série
        return chaine.replace("\n","").replace("\r","").replace("\0","")         
        
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        """
        méthode de communication via la série
        envoi d'abord au destinataire une liste de trames au périphériques 
        (celles ci sont toutes acquittées une par une pour éviter le flood)
        puis récupère nb_lignes_reponse trames sous forme de liste
        
        une liste messages d'un seul élément : ["chaine"] peut éventuellement être remplacée par l'élément simple : "chaine"  #userFriendly
        """
        
        with self.mutex:
            if not type(messages) is list:
                #permet l'envoi d'un seul message, sans structure de liste
                messages = [messages]
            
            #parcourt la liste des messages envoyés
            for message in messages:
                #print(str(message)+"<")
                self.peripheriques[destinataire].serie.write(bytes(str(message) + '\r',"utf-8"))
                #chaque envoi est acquité par le destinataire, pour permettre d'émettre en continu sans flooder la série
                acquittement = ""
                while acquittement != "_":
                    acquittement = self.clean_string(str(self.peripheriques[destinataire].serie.readline(),"utf-8"))
                    #print("\t>"+acquittement)
                    
            #liste des réponses
            reponses = []
            for i in range(nb_lignes_reponse):
                reponse = str(self.peripheriques[destinataire].serie.readline(),"utf-8")
                #print("\t>"+reponse)
                reponses.append(self.clean_string(reponse))
        return reponses
