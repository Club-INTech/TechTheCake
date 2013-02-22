import numpy
import collections
from outils_maths.point import Point
from outils_maths.vitesse import Vitesse
#on peut trouver les sources de numpy ici : http://bit.ly/13boxRp
#et les ajouter comme ca : $python3 setup.py install

class Kalman:
  
  def __init__(self,x,P,F,H,R,Q):
    self.x = x
    self.P = P
    self.F = F
    self.H = H
    self.R = R
    self.Q = Q
  
  def prediction(self, u = None):
    if u == None:
        u = numpy.zeros(self.x.shape[0])[:, numpy.newaxis]
    self.x = (self.F * self.x) + u
    self.P = self.F * self.P * self.F.transpose() + self.Q
  
  def measurement(self, Z):
    y = Z - (self.H * self.x)
    S = self.H * self.P * self.H.transpose() + self.R    
    K = self.P * self.H.transpose() * numpy.linalg.inv(S)
    self.x = self.x + (K * y)
    self.P = (numpy.identity(self.x.shape[0]) - (K * self.H)) * self.P
    
  def filtrer(self, Z, u = None):
    prediction(u)
    measurement(Z)
    
class FiltrageLaser:
    
    def __init__(self, config):
        self.config = config
        self.dt = 0.3
        x = numpy.array([1400,100,0.,0.])[:, numpy.newaxis] # vecteur d'état au départ
        P = numpy.matrix([[30.,0.,0.,0.],[0.,30.,0.,0.],[0.,0.,10.,0.],[0.,0.,0.,10.]]) # incertitude initiale
        F = numpy.matrix([[1.,0.,self.dt,0.],[0.,1.,0.,self.dt],[0.,0.,1.,0.],[0.,0.,0.,1.]]) # matrice de transition
        H = numpy.matrix([[1.,0.,0.,0.],[0.,1.,0.,0.]])# matrice d'observation
        R = numpy.matrix([[30,0.],[0.,30]]) # incertitude sur la mesure
        #Q = numpy.matrix([[self.dt**3/3., self.dt**2/2., 0, 0],[self.dt**2/2.,self.dt, 0, 0],[0,0,self.dt**3/3.,self.dt**2/2],[0,0,self.dt**2/2,self.dt]])
        #Q *= 20;
        Q = numpy.matrix([[3, 0, 0, 0],[0, 3, 0, 0],[0, 0, 3, 0],[0, 0, 0, 3]])
        self.filtre_kalman = Kalman(x, P, F, H, R, Q)
        self.historique = collections.deque(maxlen=2)
        self.valeurs_rejetees = 0
        self.acceleration = None
        
    def etat_robot_adverse(self):
        return self.filtre_kalman.x
        
    def update_dt(self, new_dt):
        self.filtre_kalman.F[1,3] = new_dt
        self.filtre_kalman.F[2,4] = new_dt
    
    def position(self):
        state = self.filtre_kalman.x
        return Point(int(state[0]), int(state[1]))
    
    def vitesse(self):
        state = self.filtre_kalman.x
        return Vitesse(int(state[2]), int(state[3]))
                
    def update(self, x, y):
        if self._filtrage_acceleration(Point(x, y)):
            self.filtre_kalman.prediction()
            self.filtre_kalman.measurement(numpy.array([x,y])[:, numpy.newaxis])
            self.historique.append(self.position())
        
    def _filtrage_acceleration(self, pointm0):
        """
        Vérifie si le point est cohérent avec la position actuelle, en basant sur l'accélération
        """
        # Pas suffisamment de valeurs précédentes pour calculer l'accélération
        if len(self.historique) != 2:
            return True
            
        # 2 derniers points valides
        pointm1 = self.historique[1]
        pointm2 = self.historique[0]
        
        # Vecteurs vitesses et accélération
        vitesse_actuelle = pointm0 - pointm1
        vitesse_precedente = pointm1 - pointm2
        acceleration = vitesse_actuelle - vitesse_precedente
        
        # Produit scalaire pour savoir s'il y a accélération ou décélération
        produit = acceleration.x * vitesse_precedente.x + acceleration.y * vitesse_precedente.y
        
        # Rejette les accélérations brutales
        if acceleration.norme() / self.dt**2 > 1000 and produit > 0 and self.valeurs_rejetees < 3:
            #print("accélération rejetée {0}, produit = {1}".format(acceleration, produit))
            self.valeurs_rejetees += 1
            return False
        else:
            self.valeurs_rejetees = 0
            return True
