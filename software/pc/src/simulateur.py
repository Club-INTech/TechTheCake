from suds.client import Client
import math

class Simulateur:

    def __init__(self, config):
        try:
            client = Client("http://localhost:8090/INTechSimulator?wsdl")
        except:
            print("\n\nle serveur de simulation est introuvable !")
            input()
        
        # Initialisation de la table
        client.service.reset()
        client.service.setTableDimension(config["table_x"], config["table_y"])
        client.service.defineCoordinateSystem(1, 0 , 0, -1, config["table_x"] / 2, config["table_y"])
        
        # Déclaration du robot
        if config["couleur"] == "bleu":
            couleur = "blue"
            ennemi = "red"
        else:
            couleur = "red"
            ennemi = "blue"
        client.service.defineRobot({"list":[
            {"float":[-config["longueur_robot"]/2,-config["largeur_robot"]/2]},
            {"float":[-config["longueur_robot"]/2,config["largeur_robot"]/2]},
            {"float":[config["longueur_robot"]/2,config["largeur_robot"]/2]},
            {"float":[config["longueur_robot"]/2,-config["largeur_robot"]/2]}
            ]},couleur)
            
        # Initialisation de la position du robot sur le simulateur
        if config["couleur"] == "bleu":
            client.service.setRobotAngle(0)
            client.service.setRobotPosition(-1200,300)
        else:
            client.service.setRobotAngle(math.pi)
            client.service.setRobotPosition(1200,300)
                    
        # Déclaration d'un robot adverse
        client.service.addEnemy(1, 80, ennemi)
                
        # Definition des zones des capteurs
        client.service.addSensor(0,{"list":[{"int":[0,-100]},{"int":[-135.,-1100.]},{"int":[135,-1100]}]}) # infrarouge arrière
        client.service.addSensor(1,{"list":[{"int":[0,100]},{"int":[-135.,1100.]},{"int":[135,1100]}]})    # infrarouge avant
        client.service.addSensor(2,{"list":[{"int":[0,-100]},{"int":[-600.,-1600.]},{"int":[600,-1600]}]}) # ultra son arrière
        client.service.addSensor(3,{"list":[{"int":[0,100]},{"int":[-600.,1600.]},{"int":[600,1600]}]})    # ultra son avant
        
        # Enregistrement du service SOAP
        self.soap = client.service
