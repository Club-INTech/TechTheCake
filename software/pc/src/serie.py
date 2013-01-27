from serial import Serial
from mutex import Mutex
import os
        
class Peripherique:
    """
    Structure décrivant un périphérique série :
    id : ping attendu de la carte (0 pour l'asservissement...)
    baudrate : (9600, 57600...).
    Si le périphérique serie associé est trouvé, un attribut serie sera créé : il contient le chemin vers le périphérique ("/dev/ttyACM0"...)
    """
    def __init__(self,id,baudrate):
        self.id = id
        self.baudrate = baudrate
        
class Serie:
    """
    Classe générique de gestion des périphériques série, utilisés via un seul service.
    Elle permet de détecter et stocker les chemins pour communiquer avec chaque carte dans des objets de la classe Peripherique.
    Elle permet d'envoyer une trame sur un périphérique et d'en recevoir une en retour.
    Des mécanismes augmentant la proofitude des échanges ont été ajoutés ;)
    """
    def __init__(self, log):
        
        #instances des dépendances
        self.log = log
        
        #mutex évitant les écritures/lectures simultanées sur la série
        self.mutex = Mutex()
        #dictionnaire des périphériques recherchés
        self.peripheriques = {"asservissement": Peripherique(0,9600),"capteurs_actionneurs" : Peripherique(3,9600), "capteur_couleur" : Peripherique(1,9600), "cadeaux" : Peripherique(6,9600), "ascenseur": Peripherique(2,9600),"pince_verre": Peripherique(8,9600), "actionneur_bougies": Peripherique(7,9600)}
        #attribution initiale des périphériques
        self.attribuer()
        self.arret_serie=False
        
    def attribuer(self):
        """
        Cette méthode invoquée au lancement du service série permet de détecter et stocker les chemins pour communiquer avec chaque carte dans des objets de la classe Peripherique.
        """
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
                    instanceSerie = Serial(source, baudrate, timeout=1.0)
                    
                    #vide le buffer série coté pc
                    instanceSerie.flushInput()
                    
                    #vide le buffer de l'avr
                    instanceSerie.write(bytes(" \r","utf-8"))
                    instanceSerie.readline()
                    
                    #ping
                    instanceSerie.write(bytes("?\r","utf-8"))
                    #évacuation de l'acquittement
                    instanceSerie.readline()
                    #réception de l'id de la carte
                    rep = self._clean_string(str(instanceSerie.readline(),"utf-8"))
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
                self.peripheriques[destinataire].serie = Serial(source, self.peripheriques[destinataire].baudrate, timeout=1.0)
            else:
                self.log.warning(destinataire+" non trouvé !")
        
    def _clean_string(self, chaine):
        """
        supprime des caractères spéciaux sur la chaine
        """
        return chaine.replace("\n","").replace("\r","").replace("\0","")         
        
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        """
        Méthode de communication via la série.
        Envoie d'abord au destinataire une liste de trames au périphériques 
        (celles ci sont toutes acquittées une par une pour éviter le flood),
        puis récupère nb_lignes_reponse trames sous forme de liste.
        
        Une liste messages d'un seul élément : ["chaine"] peut éventuellement être remplacée par l'élément simple : "chaine".  #userFriendly
        """
        with self.mutex:
            if not self.arret_serie:
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
                        acquittement = self._clean_string(str(self.peripheriques[destinataire].serie.readline(),"utf-8"))
                        #print("\t a>"+destinataire+acquittement)
                        
                #liste des réponses
                reponses = []
                for i in range(nb_lignes_reponse):
                    reponse = str(self.peripheriques[destinataire].serie.readline(),"utf-8")
                    #print("\t r>"+destinataire+reponse)
                    reponses.append(self._clean_string(reponse))
        return reponses

    def set_arret_serie(self):
        """
        Méthode pour arrêter le service série, appelée par le service timer à la fin du match.
        """
        with self.mutex:
            self.arret_serie=True
        
