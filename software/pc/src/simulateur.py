from suds.client import Client
import math
import logging

class Simulateur:

    def __init__(self, config):
        try:
            client = Client("http://" + config["simulateur_hote"] + ":8090/INTechSimulator?wsdl")
        except:
            print("\n\nle serveur de simulation est introuvable !")
            input()
        
        # Initialisation de la table
        client.service.reset()
        client.service.setTableDimension(config["table_x"], config["table_y"])
        client.service.defineCoordinateSystem(1, 0 , 0, -1, config["table_x"] / 2, config["table_y"])
        
        # Couleur du robot
        if config["couleur"] == "bleu":
            couleur = "blue"
            ennemi = "red"
        else:
            couleur = "red"
            ennemi = "blue"
            
        ## Définition d'un robot carré
        #client.service.defineRobot({"list":[
            #{"float":[-config["longueur_robot"]/2,-config["largeur_robot"]/2]},
            #{"float":[-config["longueur_robot"]/2,config["largeur_robot"]/2]},
            #{"float":[config["longueur_robot"]/2,config["largeur_robot"]/2]},
            #{"float":[config["longueur_robot"]/2,-config["largeur_robot"]/2]}
            #]},couleur)
            
        # Définition du robot réel
        client.service.defineRobot({"list":[
            {"float":[-105.,-120.]},
            {"float":[-150.,-75.]},
            {"float":[-150.,75.]},
            {"float":[-105.,120.]},
            {"float":[105.,120.]},
            {"float":[150.,75.]},
            {"float":[150.,-75.]},
            {"float":[105.,-120.]},
            ]},couleur)
            
        # Definition des zones des capteurs
        client.service.addSensor(0,{"list":[{"int":[0,-config["largeur_robot"]/2]},{"int":[-135.,-1100.]},{"int":[135,-1100]}]}) # infrarouge arrière
        client.service.addSensor(1,{"list":[{"int":[0,config["largeur_robot"]/2]},{"int":[-135.,1100.]},{"int":[135,1100]}]})    # infrarouge avant
        client.service.addSensor(2,{"list":[{"int":[0,-config["largeur_robot"]/2]},{"int":[-600.,-1600.]},{"int":[600,-1600]}]}) # ultra son arrière
        client.service.addSensor(3,{"list":[{"int":[0,config["largeur_robot"]/2]},{"int":[-600.,1600.]},{"int":[600,1600]}]})    # ultra son avant
            
        # Définitions des obstacles
        client.service.addRectangleObstacle(-1500, 100, 400, 100, "white", False)
        client.service.addRectangleObstacle(-1500, 2000, 400, 100, "white", False)
        client.service.addRectangleObstacle(1100, 100, 400, 100, "white", False)
        client.service.addRectangleObstacle(1100, 2000, 400, 100, "white", False)
        client.service.addCircleObstacle(0, 2000, 500, "rose", True)
        
        # Initialisation de la position du robot sur le simulateur
        if config["couleur"] == "bleu":
            client.service.setRobotAngle(0)
            client.service.setRobotPosition(-1350,600)
        else:
            client.service.setRobotAngle(math.pi)
            client.service.setRobotPosition(1350,600)
                    
        # Déclaration d'un robot adverse
        if config["activer_ennemi_principal"]:
            client.service.addEnemy(0, 40, ennemi)
            client.service.addEnemy(1, 40, ennemi)
        
        # Enregistrement du service SOAP
        self.soap = client.service
        
        # Affichage des logs suds de niveau critique seulement
        logging.getLogger('suds.client').setLevel(logging.CRITICAL)
