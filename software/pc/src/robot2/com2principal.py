import socket

class Com2principal:
    """
    Classe implémentant la communication avec le robot principal
    """
    def __init__(self, config, log, robot):

        self.config = config
        self.log = log
        self.robot = robot
        
        self._connection_robot()
        
    def _connection_robot(self):
        # Ouverture de la socket
        self.robot1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.robot1_socket.settimeout(self.config["timeout_socket_robots"])
        self.robot1_socket.connect((self.config["ip_robot_principal"], 4242))
        
        
    def _ask(self, message, lgr_rep=1):
        self.robot1_socket.send(bytes(message+"\n", 'UTF-8'))
        reponse = []
        for i in range(lgr_rep):
            reponse.append(str(self.robot1_socket.recv(15),"utf-8").replace("\n",""))
        return reponse
        
    def _fermeture_socket(self):
        self.robot1_socket.close()
        
    #####################################################"
    
    def demarrage_match(self):
        return self._ask("debut")[0]
        
    def zone_action_robot1(self):
        return self._ask("zone")[0]
        
    def nb_cases_depart_adverse(self):
        return self._ask("nb_cases")[0]
        
    def cases_depart_adverse(self, nb_cases):
        return self._ask("cases", nb_cases)
        
    