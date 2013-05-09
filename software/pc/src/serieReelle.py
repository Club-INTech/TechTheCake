from serial import Serial
from mutex import Mutex
import os
import time
        
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
        
class SerieReelle:
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

        #les threads attendent la serie
        self.prete = False
        
    def definir_peripheriques(self, dico_infos_peripheriques):
        #dictionnaire des périphériques recherchés : recrée les objets périphériques à partir des données fournies
        self.peripheriques = dict(map(lambda c: (c[0],Peripherique(*c[1][0])),dico_infos_peripheriques.items()))
        
    def attribuer(self):
        """
        Cette méthode invoquée au lancement du service série permet de détecter et stocker les chemins pour communiquer avec chaque carte dans des objets de la classe Peripherique.
        """
        #liste les chemins trouvés dans /dev
        sources = os.popen('ls -1 /dev/ttyUSB* 2> /dev/null').readlines()
        sources.extend(os.popen('ls -1 /dev/ttyACM* 2> /dev/null').readlines())
        
        for k in range(len(sources)):
            sources[k] = sources[k].replace("\n","")
        
        #liste les baudrates des périphériques recherchés
        baudrates = []
        for destinataire in (self.peripheriques):
            if not self.peripheriques[destinataire].baudrate in baudrates:
                baudrates.append(self.peripheriques[destinataire].baudrate)
        
        #recherche les pings présents sur les chemins et baudrates listés
        deja_attribues = []
        
        pings = {}
        for baudrate in baudrates:
            print("liste des pings pour le baudrate "+str(baudrate)+" :")
            k=0
            while k < len(sources):
                if not k in deja_attribues:
                    try:
                        instanceSerie = Serial(sources[k], baudrate, timeout=0.1)
                        
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
                            pings[id]=sources[k]
                            print(" * "+str(id)+" sur "+sources[k])
                            deja_attribues.append(k)
                        except:
                            pass
                    except Exception as e:
                        self.log.warning("exception durant la détection des périphériques série: {0}".format(e))
                k += 1
                    
        #attribue les instances de série pour les périphériques ayant le bon ping
        for destinataire in (self.peripheriques):
            if self.peripheriques[destinataire].id in pings:
                source = pings[self.peripheriques[destinataire].id]
                self.log.debug(destinataire+" OK sur "+source)
                self.peripheriques[destinataire].chemin = source
                self.peripheriques[destinataire].serie = Serial(source, self.peripheriques[destinataire].baudrate, timeout=1.0)
            else:
                self.log.warning(destinataire+" non trouvé !")

        time.sleep(1)
        self.prete= True
        
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
            if not type(messages) is list:
                #permet l'envoi d'un seul message, sans structure de liste
                messages = [messages]
            
            #parcourt la liste des messages envoyés
            for message in messages:
                #print("message : >"+str(message)+"<")#DEBUG
                try:
                    self.peripheriques[destinataire].serie.write(bytes(str(message) + '\r',"utf-8"))
                except Exception as e:
                    self.log.warning(
                        "exception lors de la tentative d'envoi du message {0} à la carte {1}: {2}"
                        .format(message, destinataire, e)
                    )
                    return None
                    
                #chaque envoi est acquité par le destinataire, pour permettre d'émettre en continu sans flooder la série
                try:
                    acquittement = ""
                    while acquittement != "_":
                        acquittement = self._clean_string(str(self.peripheriques[destinataire].serie.readline(),"utf-8"))
                        #print("\t acquittement de "+destinataire+" : >"+acquittement+"<")#DEBUG
                        
                        if acquittement == "":
                            self.peripheriques[destinataire].serie.write(bytes(str(message) + '\r',"utf-8"))
                            
                except Exception as e:
                    self.log.warning(
                        "exception lors de la lecture de la réponse au message {0} à la carte {1}: {2}"
                        .format(message, destinataire, e)
                    )
                    return None
                    
            #liste des réponses
            reponses = []
            for i in range(nb_lignes_reponse):
                reponse = str(self.peripheriques[destinataire].serie.readline(),"utf-8")
                #print("\t r>"+destinataire+reponse)
                reponses.append(self._clean_string(reponse))
        return reponses

    def serie_prete(self):
        return self.prete
