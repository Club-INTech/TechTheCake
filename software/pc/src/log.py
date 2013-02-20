import os,sys
import datetime
import logging

# Couleurs pour le fun et surtout pour ... le fun
def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        # Si on n'écrit pas dans le fichier, on ajoute des couleurs
        if not isinstance(args[0], logging.FileHandler) :
            levelno = args[1].levelno
            if(levelno>=50): # CRITICAL
                color_msg = '\x1b[31m' # red
                color_levelname = '\033[1;31m'
            elif(levelno>=30): # WARNING
                color_msg = '\x1b[33m' # magenta
                color_levelname = '\033[1;33m'
            elif(levelno>=10): # DEBUG
                color_msg = '\x1b[32m' # cyan
                color_levelname = '\033[1;32m'
            else: # NOTSET
                color_msg = '\x1b[0m' # normal
                color_levelname = '\x1b[0m'
        
            args[1].msg = color_msg + str(args[1].msg) +  '\x1b[0m'  # normal
            args[1].levelname = color_levelname + args[1].levelname + '\x1b[0m'
        return fn(*args)
        
        
    return new

# Ne fonctionne pas sur Windows mais de toute façon on s'en balance de Windaube
logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

class Log:
    """
    Classe permettant de gérer les logs.
    A besoin d'une instance Config pour se lancer (fournie par l'injecteur de dépendances).
    Après avoir été instanciée, la methode self.set_chemin(chemin) doit être appellée,
    afin de fournir à la classe le chemin vers le dossier où seront enregistrés les logs.
    (si cette méthode n'est pas appellée, les logs ne fonctionneront pas).
    
    Une fois tous ces préparatifs faits, l'utilisateur peut appeller 3 niveaux de log :
    Log.debug(message)      ---> Message de débug.             (DEBUG)
    Log.warning(message)    ---> Message d'avertissement.      (WARNING)
    Log.critical(message)   ---> Message d'erreur critique.    (CRITICAL)
    
    """
    def __init__(self, config):
        self.config             = config
        self.nom                = self.config["log_nom"]
        self.logs               = self.config["log_sauvegarde"]
        self.stderr             = self.config["log_affichage"]
        self.logs_level         = self.config["log_level_sauvegarde"]
        self.stderr_level       = self.config["log_level_affichage"]
        self.logs_format        = self.config["log_format_sauvegarde"]
        self.stderr_format      = self.config["log_format_affichage"]
        self.dossier            = self.config["log_nom_dossier"]
        self.dossier_tmp        = self.config["log_nom_dossier_tmp"]
        self.taille_dossier_tmp = self.config["log_maxsize_tmp"]
        self.ramdisk            = self.config["log_ramdisk"]
        self.initialisation()

    def initialisation(self):
        self.levels = ('DEBUG', 'WARNING', 'CRITICAL')
        if not (self.logs_level in self.levels and self.stderr_level in self.levels):
            raise Exception("Erreur sur les noms de logs")
        
        if not (self.logs in (0,1) and self.stderr in (0,1) and self.ramdisk in (0,1)) :
            raise Exception("Erreur sur les attributs log_affichage, log_sauvegarde, ramdisk de config.ini")
        
        # Création du logger
        self.logger = logging.getLogger(self.nom)
        
        # Raccourcis.
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.critical = self.logger.critical
        
        self.logger.setLevel(logging.DEBUG)
 
    
    def set_chemin(self, dossier_racine) :
        """
        Permet d'ajouter aux logs la cible du fichier d'enregistrement.
        
        """
        self.dossier_racine     = dossier_racine
        self.dossier_abs        = os.path.join(self.dossier_racine, self.dossier)
        self.dossier_tmp_abs    = os.path.join(self.dossier_abs, self.dossier_tmp)
        
        self.revision_disponible()
        
        self.nom_fichier_log    = os.path.join(self.dossier_abs, str(self.revision)+".log")
        self.nom_fichier_tmp    = os.path.join(self.dossier_tmp_abs, "TMP")
        
        if self.logs:
            # Ajout du handler pour logs
            self.configurer_logs()
            
        if self.stderr:
            # Ajout du handler pour stderr
            self.configurer_stderr()
 
    def creer_dossier(self):
        """
        Crée un dossier si il n'existe pas déjà
        Crée aussi le dossier tmp~ pour le ramdisk
        """
        # Dossier de logs
        if not os.access(self.dossier_abs, os.F_OK):
            os.makedirs(self.dossier_abs)
        # Dossier ramdisk
        if not os.access(self.dossier_tmp_abs, os.F_OK) :
            os.makedirs(self.dossier_tmp_abs)
        
        # Montage du dossier ramdisk en RAM
        if self.ramdisk:
            os.system("sudo mount -t tmpfs -o size=" + self.taille_dossier_tmp + " tmpfs " + self.dossier_tmp_abs)
        
        
    def revision_disponible(self):
        """
        Donne la prochaine révision à créer dans les logs
        
        :param dossier: dossier principal des logs
        :type dossier: string
        :return: révision à créer
        :rtype: int
        """
        if not hasattr(self, "revision") :
            i = 0
            self.creer_dossier()
            while os.path.exists(os.path.join(self.dossier_abs, str(i)+".log")):
                i += 1
            self.revision = i
    
    def configurer_logs(self):
        """
        Configure les logs (FICHER)
        """
        if hasattr(self, 'logs_handler'):
            self.logger.removeHandler(self.logs_handler)
        self.logs_handler = logging.FileHandler(self.nom_fichier_tmp)
        exec("self.logs_handler.setLevel(logging."+self.logs_level+")")
        formatter = logging.Formatter(self.logs_format)
        self.logs_handler.setFormatter(formatter)
        self.logger.addHandler(self.logs_handler)
    
    def configurer_stderr(self):
        """
        Configure la sortie stderr (CONSOLE)
        """
        if hasattr(self, 'stderr_handler'):
            self.logger.removeHandler(self.stderr_handler)
        self.stderr_handler = logging.StreamHandler()
        exec("self.stderr_handler.setLevel(logging."+self.stderr_level+")")
        formatter = logging.Formatter(self.stderr_format, "%Hh%Mm%Ss")
        self.stderr_handler.setFormatter(formatter)
        self.logger.addHandler(self.stderr_handler)
        
    def flush(self) :
        """
        Flushe la sortie dans le disque dur. A appeller en fin de match.        
        """
        self.logs_handler.close()
        
        f_tmp = open(self.nom_fichier_tmp, "r")
        f_log = open(self.nom_fichier_log, "w")
        f_log.write(f_tmp.read())
        f_log.close()
        f_tmp.close()

class LogTest:
    
    def debug(self, message):
        pass
        
    def warning(self, message):
        pass
        
    def critical(self, message):
        pass
