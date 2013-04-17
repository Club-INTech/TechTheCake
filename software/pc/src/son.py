from random import randint
import pygame.mixer
import time

class Son:
    """
    Classe gérant les sons.
    """
    def __init__(self, config, log):
        pygame.init()
        self.log = log
        self.config = config
        self.date_dernier = 0
        self.sons = {
            # Ennemi détecté
            "detection": [pygame.mixer.Sound("sons/Turret_sp_sabotage_factory_good_pass01_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_autosearch_5_fr.wav")],

            # Exception mouvement impossible
            "blocage": [pygame.mixer.Sound("sons/Turret_turret_disabled_5_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_disabled_6_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_fizzler_1_fr.wav"), pygame.mixer.Sound("sons/Defective_Turret_sp_sabotage_factory_defect_fail18_fr.wav")],

            # Début du match
            "debut": [pygame.mixer.Sound("sons/Turret_turret_deploy_2_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_active_5_fr.wav")],

            # Avant la fin
            "compte_rebours": [pygame.mixer.Sound("sons/GLaDOS_testchambermisc34_fr.wav")],

            # Fin
            "generique": [pygame.mixer.Sound("sons/generique.ogg")],

            # Random
            "random": [pygame.mixer.Sound("sons/Space_core_space04_fr.wav"), pygame.mixer.Sound("sons/Space_core_space21_fr.wav"), pygame.mixer.Sound("sons/Space_core_space23_fr.wav")]
    }

    def jouer(self, id, force=False):
        """
        Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
        """
    #un timer pour ne pas être trop bavard?
    
        try:
            if self.config["musique"] and (time.time()-self.date_dernier > self.config["intervalle_entre_sons"] or force):
                self.date_dernier = time.time()
                taille = len(self.sons[id])
                pygame.mixer.stop()
                self.sons[id][randint(0,taille-1)].play()
        except Exception as e:
            self.log.warning("Erreur service de son: "+str(e))

