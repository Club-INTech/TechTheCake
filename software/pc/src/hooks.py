from math import pi
       
_tolerance_distance_mm   = 30
_tolerance_angle_radians = 0.2

class Hook:
    def __init__(self,callback,args):
        #instance du robot #TODO
        self.robot = container.provide(Robot)
        #méthode à appeler
        self.callback = callback
        #arguments facultatifs pour le callback
        self.args = args
    
class Hook_position(Hook):
    def __init__(self, position, callback,*args):
        Hook.__init__(self,callback,args)
        #point déclencheur
        self.position_hook = position
    def evaluate(self):
        if ((self.robot.x - self.position_hook.x)**2 + (self.robot.y - self.position_hook.y)**2 <= _tolerance_distance_mm**2)
            self.callback(*self.args)
        
class Hook_orientation(Hook):
    def __init__(self, orientation, callback,*args):
        Hook.__init__(self,callback,args)
        #angle déclencheur
        self.orientation_hook = orientation
    def evaluate(self):
        delta_angle = abs(self.robot.orientation - self.orientation_hook)%(2*pi)
        if (delta_angle > pi): delta_angle = (2*pi)-delta_angle
        if (delta_angle <= _tolerance_angle_radians)
            self.callback(*self.args)
            
class Hook_temps(Hook):
    def __init__(self, temps, callback,*args):
        Hook.__init__(self,callback,args)
        #timestamp déclencheur
        self.temps_hook = temps
    def evaluate(self):
        if (self.robot.duree_jeu >= self.temps_hook):
            self.callback(*self.args)