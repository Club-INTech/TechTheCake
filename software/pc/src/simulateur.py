#client SOAP pour le simulateur
from suds.client import Client


from mutex import Mutex


class Simulateur():
  
    def __init__(self,config,log):
        client=Client("http://localhost:8090/INTechSimulator?wsdl")
        self.service=client.service
        #services utilisés
        self.config = config
        self.log = log
            
        #mutex d'envoi au serveur SOAP
        self.mutex = Mutex()
            
            
        #initialisation de la table TODO : prendre les valeurs dans Table
        self.service.reset()
        self.service.setTableDimension(3000,2000)
        self.service.defineCoordinateSystem(1,0,0,-1,1500,2000)
        self.service.defineRobot({"list":[{"float":[-200.,-200.]},{"float":[-200.,200.]},{"float":[200.,200.]},{"float":[200.,-200.]}]})
        self.service.defineRobotSensorZone({"list":[{"int":[0,400]},{"int":[-500.,1000.]},{"int":[500,1000]}]})
        self.service.setRobotAngle(0)
        self.service.setRobotPosition(-1200,300)
        self.service.addEnemy(30,"black")

   
    def gestion_blocage(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        méthode de détection des collisions
        retourne True si la valeur du booléen blocage (attribut de robot) doit etre remplacée par True
        """
        with self.mutex:
            return self.service.isBlocked()
    
    def update_enMouvement(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        cette méthode détermine si le robot est arrivé à sa position de consigne
        retourne la valeur du booléen enMouvement (attribut de robot)
        """
        with self.mutex:
            return self.service.isMoving() or self.service.isTurning()
    
    def get_infos_stoppage_enMouvement(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        """
        return {}
        
    def est_bloque(self):
        with self.mutex:
            return self.service.isBlocked()
        
    def est_arrive(self):
        with self.mutex:
            return not(self.service.isMoving() or self.service.isTurning())
    
    def get_infos_x_y_orientation(self):
        """
        UTILISÉ UNIQUEMENT PAR LE THREAD DE MISE À JOUR
        """
        with self.mutex:
            return [self.service.getX(), self.service.getY(), self.service.getAngle()]
            
            
    def avancer(self, distance):
        try:
            with self.mutex:
                self.service.moveRobot(distance)
        except Exception as e:
            print(e)

    def tourner(self, angle):
        try:
            with self.mutex:
                self.service.turnRobot(angle, True)
        except Exception as e:
            print(e)
      
    
    def stopper(self):
        with self.mutex:
            self.service.stopRobot() 
          
    def mesurer(self):
        with self.mutex:
            return self.service.getRobotSensorValue()
            