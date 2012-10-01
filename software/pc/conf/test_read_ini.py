import configparser


# Classe permettant l'ouverture et la compréhension du fichier pc/conf/conf.ini
# L'instanciation de cet objet a besoin du chemin pc/conf/ pour se lancer
class Config :
    def __init__(self, chemin) :
        if not hasattr(Config, "_is_initialized") :
            Config._is_initialized = True
            Config._chemin = _get_chemin(chemin)   
            
            Config._conf  = configparser.ConfigParser()
            Config._conf.readfp(open(Config._chemin + "conf.ini"))
            Config._mode   = None
            Config._dic    = {}
        
    def __getitem__(self, key) :
        return Config._dic[key]
        
    # Enregistre le mode utilisé dans le fichier de conf.
    def _get_mode(self) :
        Config._mode = Config._conf.get("global", "mode")
        
    # Charge en mémoire des variables de configuration
    def get_vars(self) :
        if Config._mode is None :
            self._get_mode()
        Config._dic = {}
        # Chargement des valeurs par défaut
        for var in Config._conf.items("default") :
            Config._dic[var[0]] = _try_to_cast(var[1])
        # Écrasement de celles-ci si le profil chargé n'est pas celui
        # par défaut.
        if Config._mode != "default" :
            for var in Config._conf.items(Config._mode) :
                Config._dic[var[0]] = _try_to_cast(var[1])
        
# Classe permettant l'acquisition des différentes constantes
class Constantes :
    def __init__(self, chemin) :
        if not hasattr(Constantes, "_is_initialized") :
            Constantes._is_initialized = True
            Constantes._chemin = _get_chemin(chemin)
            Constantes._conf   = configparser.ConfigParser()
            Constantes._conf.readfp(open(Constantes._chemin + "constantes.ini"))
               
    
    def __getitem__(self, key) :
        return Constantes._dic[key]
        
    # Charge en mémoire le dictionnaire de constantes   
    def get_vars(self) :
        sections = Constantes._conf.sections()
        Constantes._dic = {}
        for section in sections :
            Constantes._dic[section] = {}
            for var in Constantes._conf.items(section) :
                Constantes._dic[section][var[0]] = _try_to_cast(var[1])
        
# Retourne un chemin valide complété si besoin avec un "/" final.
def _get_chemin(chemin) :
    if chemin[-1] not in ['\\', "/"] :
        chemin += "/"
    return chemin
    
# NE JAMAIS PARLER DE CETTE FONCTION À MARC /!\ /!\ /!\
def _try_to_cast(var) :
    try : return int(var)
    except ValueError :
        try : return float(var)
        except ValueError : return var
        