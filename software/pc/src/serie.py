from serial import Serial
from mutex import Mutex
import os
from time import sleep
        
        
class Peripherique:
    def __init__(self,id,baudrate):
        self.id = id
        self.baudrate = baudrate
        
class Serie:
        
    def __init__(self):
        self.mutex = Mutex()
        self.peripheriques = {"asservissement": Peripherique(0,9600),"capteurs_actionneurs" : Peripherique(3,9600)}
        self.attribuer()
        
    def attribuer(self):
        #listage des périphériques trouvés
        sources = os.popen('ls -1 /dev/ttyUSB* 2> /dev/null').readlines()
        sources.extend(os.popen('ls -1 /dev/ttyACM* 2> /dev/null').readlines())
        for k in range(len(sources)):
            sources[k] = sources[k].replace("\n","")
        
        for destinataire in (self.peripheriques):
            for source in sources:
                try:
                    print("##("+destinataire+", "+source+"############################")
                    instanceSerie = Serial(source, self.peripheriques[destinataire].baudrate, timeout=0.5)
                    
                    #vide le buffer de l'avr
                    instanceSerie.write(bytes("\r","utf-8"))
                    
                    instanceSerie.write(bytes("?\r","utf-8"))
                    rep = str(instanceSerie.readline(),"utf-8")
                    print(self.clean_string(rep)+" -- "+str(self.peripheriques[destinataire].id))
                    if self.clean_string(rep) == str(self.peripheriques[destinataire].id):
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print(destinataire+"\tOK sur "+source)
                        self.peripheriques[destinataire].chemin = source
                        self.peripheriques[destinataire].serie = instanceSerie
                        sources.remove(source)
                        break
                    else:
                        instanceSerie.close()
                        #del instanceSerie
                except Exception as e:
                    print(e)
        
    def clean_string(self, chaine):
        return chaine.replace("\n","").replace("\r","").replace("\0","") 
    
    def communiquer(self, destinataire, messages, nb_lignes_reponse):
        with self.mutex:
           #un seul message
            if not hasattr(messages, "__getitem__"):
                self.peripheriques[destinataire].serie.write(bytes(str(messages) + '\r',"utf-8"))
            else:
            #liste de messages
                for message in messages:
                    sleep(0.1)
                    self.peripheriques[destinataire].serie.write(bytes(str(message) + '\r',"utf-8"))
                    
            #liste des réponses
            reponses = []
            for i in range(nb_lignes_reponse):
                sleep(0.1)
                reponse = self.clean_string(str(self.peripheriques[destinataire].serie.readline(),"utf-8"))
                reponses.append(reponse)
        return reponses
        