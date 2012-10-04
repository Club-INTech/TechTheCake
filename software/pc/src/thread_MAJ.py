from time import sleep
from robot import Robot
from serie import Serie
from log import Log

def fonction_MAJ(container):
    serie = container.get_service(Serie)
    robot = container.get_service(Robot)
    log = container.get_service(Log)
    
    print(robot.acquittement is robot.arrived)
    while 42:
        #if robot.acquittement is robot.arrived:
            #robot.acquittement = robot.stopped
        
        PWMmoteurGauche,PWMmoteurDroit,derivee_erreur_rotation,derivee_erreur_translation = serie.communiquer("asservissement","?bloc",4)
        print("#######")
        print(PWMmoteurGauche)
        print(PWMmoteurDroit)
        print(derivee_erreur_rotation)
        print(derivee_erreur_translation)
        sleep(0.5)