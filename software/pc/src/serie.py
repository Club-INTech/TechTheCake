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
        self.peripheriques = {"asservissement": Peripherique(0,9600),"capteurs_actionneurs" : Peripherique(3,9600)}
        #attribution initiale des périphériques
        self.attribuer()
        
    def attribuer(self):
        #listage des périphériques trouvés dans /dev
        sources = os.popen('ls -1 /dev/ttyUSB* 2> /dev/null').readlines()
        sources.extend(os.popen('ls -1 /dev/ttyACM* 2> /dev/null').readlines())
        for k in range(len(sources)):
            sources[k] = sources[k].replace("\n","")
        
        for destinataire in (self.peripheriques):
            for source in sources:
                try:
                    print("---> recherche de "+destinataire+" sur "+source)
                    instanceSerie = Serial(source, self.peripheriques[destinataire].baudrate, timeout=0.1)
                    
                    #vide le buffer de l'avr
                    instanceSerie.write(bytes("\r","utf-8"))
                    sleep(0.1)
                    
                    instanceSerie.write(bytes("?\r","utf-8"))
                    instanceSerie.readline()
                    rep = str(instanceSerie.readline(),"utf-8")
                    print("recu : >"+self.clean_string(rep)+"<"+" / attendu : >"+str(self.peripheriques[destinataire].id)+"<")
                    if self.clean_string(rep) == str(self.peripheriques[destinataire].id):
                        self.log.debug(destinataire+"\tOK sur "+source)
                        self.peripheriques[destinataire].chemin = source
                        self.peripheriques[destinataire].serie = instanceSerie
                        sources.remove(source)
                        break
                    else:
                        instanceSerie.close()
                except Exception as e:
                    print(e)
            if not "serie" in self.peripheriques[destinataire].__dict__:
                self.log.warning(destinataire+"\tnon trouvé !")
        
    def clean_string(self, chaine):
        #suppressions des caractères spéciaux sur la série
        return chaine.replace("\n","").replace("\r","").replace("\0","") 
    
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        with self.mutex:
            if not type(messages) is list:
                #permet l'envoi d'un seul message, sans structure de liste
                messages = [messages]
            #parcourt la liste des messages envoyés
            for message in messages:
                self.peripheriques[destinataire].serie.write(bytes(str(message) + '\r',"utf-8"))
                #chaque envoi est acquité par le destinataire, pour permettre d'émettre en continu sans flooder la série
                self.peripheriques[destinataire].serie.readline()
                    
            #liste des réponses
            reponses = []
            for i in range(nb_lignes_reponse):
                reponse = str(self.peripheriques[destinataire].serie.readline(),"utf-8")
                reponses.append(self.clean_string(reponse))
        return reponses