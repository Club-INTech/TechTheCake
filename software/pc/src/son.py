from random import randint
import time
try:
    import pygame.mixer
    pygame_ok = True
except:
    pygame_ok = False

class Son:
    """
    Classe gérant les sons.
    """
    def __init__(self, config, log):
        self.log = log
        self.config = config
        if pygame_ok and self.config["musique"]:
            self.log.debug("Chargement sons.")
            pygame.init()
            self.sons = {
                # Ennemi détecté
                "detection": [pygame.mixer.Sound("sons/Turret_sp_sabotage_factory_good_pass01_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_autosearch_5_fr.wav"), pygame.mixer.Sound("sons/Turret_sp_sabotage_factory_good_prerange01_fr.wav")],

                # Exception mouvement impossible
                "blocage": [pygame.mixer.Sound("sons/Turret_turret_disabled_5_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_disabled_6_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_fizzler_1_fr.wav"), pygame.mixer.Sound("sons/Defective_Turret_sp_sabotage_factory_defect_fail18_fr.wav")],

                # Début du match
                "debut": [pygame.mixer.Sound("sons/Turret_turret_deploy_2_fr.wav"), pygame.mixer.Sound("sons/Turret_turret_active_5_fr.wav")],

                # Avant la fin
                "compte_rebours": [pygame.mixer.Sound("sons/GLaDOS_testchambermisc34_fr.wav")],

                # Fin
                "generique": [pygame.mixer.Sound("sons/generique.ogg"), pygame.mixer.Sound("sons/radio.ogg"), pygame.mixer.Sound("sons/still_alive.ogg")],

                # Random
                "random": [pygame.mixer.Sound("sons/Space_core_space04_fr.wav"), pygame.mixer.Sound("sons/Space_core_space21_fr.wav"), pygame.mixer.Sound("sons/GLaDOS_potatos_longfall_speech03_fr.wav")]
        }
            self.log.debug("Sons chargés.")
        else:
        # Si on a un problème avec pygame, on atteint simplement la musique
            self.config["musique"] = 0
            if not pygame_ok:
                self.log.critical("Pygame introuvable (voir http://pythonfun.wordpress.com/2011/08/08/installing-pygame-with-python-3-2-on-ubuntu-11-04/). Service de son ignoré.")
        self.date_dernier = -100

    def jouer(self, id, force=False, enBoucle=False):
        """
        Boucle qui gère la stratégie, en testant les différents scripts et en exécutant le plus avantageux
        """
    #un timer pour ne pas être trop bavard?
    
        try:
            if self.config["musique"] and (time.time()-self.date_dernier > self.config["intervalle_entre_sons"] or force):
                self.date_dernier = time.time()
                taille = len(self.sons[id])
                pygame.mixer.stop()
                if enBoucle:
                    self.sons[id][randint(0,taille-1)].play(loops=-1)
                else:
                    self.sons[id][randint(0,taille-1)].play()

        except Exception as e:
            self.log.warning("Erreur service de son: "+str(e))

