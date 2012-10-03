import configparser
import os.path

_nom_fichier_conf           = "config"
_nom_fichier_constantes     = "constantes"
_extension                  = ".ini"


# Classe permettant l'ouverture et la compréhension du fichier pc/conf/conf.ini
# L'instanciation de cet objet a besoin du chemin pc/conf/ pour se lancer
class Config :
    def __init__(self) :
        self._conf  = configparser.ConfigParser()
        self._mode   = None
        
    def set_chemin(self, chemin) :
        self._chemin = chemin
        self._conf.readfp(open(os.path.join(self._chemin,  _nom_fichier_conf + _extension)))
        self.get_vars()
        
    # Fonction d'accessibilité.
    def __getitem__(self, key) :
        return self._dic[key]
        
    # Enregistre le mode utilisé dans le fichier de conf.
    def _get_mode(self) :
        self._mode = self._conf.get("global", "mode")
        
    # Retourne le mode du fichier de conf.
    def get_mode(self) :
        if self._mode is  None :
            self._get_mode()
        return self._mode

    # Charge en mémoire des variables de configuration
    def get_vars(self) :
        if self._mode is None :
            self._get_mode()
        self._dic = {}
        # Chargement des valeurs par défaut
        for var in self._conf.items("default") :
            self._dic[var[0]] = _try_to_cast(var[1])
        # Écrasement de celles-ci si le profil chargé n'est pas celui
        # par défaut.
        if self._mode != "default" :
            for var in self._conf.items(self._mode) :
                self._dic[var[0]] = _try_to_cast(var[1])
        
# Classe permettant l'acquisition des différentes constantes
# WARNING Cette classe n'est actuellement plus utilisée
#class Constantes :
    #def __init__(self, chemin) :
            #self._chemin = chemin
            #self._conf   = configparser.ConfigParser()
            #self._conf.readfp(open(os.path.join(self._chemin, _nom_fichier_constantes + _extension)))
            
    #def __getitem__(self, key) :
        #return self._dic[key]
        
    ## Charge en mémoire le dictionnaire de constantes   
    #def get_vars(self) :
        #sections = self._conf.sections()
        #self._dic = {}
        #for section in sections :
            #self._dic[section] = {}
            #for var in self._conf.items(section) :
                #self._dic[section][var[0]] = _try_to_cast(var[1])
        
# NE JAMAIS PARLER DE CETTE FONCTION À MARC /!\ /!\ /!\
def _try_to_cast(var) :
    try : return int(var)
    except ValueError :
        try : return float(var)
        except ValueError : return var
        