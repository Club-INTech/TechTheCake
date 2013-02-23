import configparser
import os.path

_nom_fichier_conf           = "config"
_nom_fichier_local 			= "local"
#_nom_fichier_constantes     = "constantes"
_extension                  = ".ini"


# Classe permettant l'ouverture et la compréhension du fichier pc/conf/conf.ini
# L'instanciation de cet objet a besoin du chemin pc/conf/ pour se lancer
class Config :
    def __init__(self) :
        self._conf  = configparser.ConfigParser()
        self._local = configparser.ConfigParser()
        self._dic = {}
        
    def set_chemin(self, chemin) :
        self._chemin = chemin
        self._conf.readfp(open(os.path.join(self._chemin,  _nom_fichier_conf + _extension)))
        
        # On teste si il y a un fichier de config local. Si il n'existe pas on le créé et on
        # crée son squelette basique, et on met self._local à None.
        try :
            with open((os.path.join(self._chemin, _nom_fichier_local + _extension)), "r") as file_local : self._local.readfp(file_local)
        except IOError :
            self._local = None
            with open((os.path.join(self._chemin, _nom_fichier_local + _extension)), "w") as file_local_ :
                file_local_.write("""# Ce fichier est un fichier généré par le programme.\n# Vous pouvez redéfinir les variables de config.ini dans ce fichier dans un mode de votre choix.\n# PS : SopalINT RULEZ !!!\n[global]\nmode=mode1\n\n[mode1]\ntemps_match=90\n\n[mode2]\ntemps_match=100\n""")
        # On charge tout en mémoire.			
        self.get_vars()
        
    # Fonction d'accessibilité.
    def __getitem__(self, key) :
        return self._dic[key]
        
    # Possibilité de réecrire la config (genre pour y construire un tableau)
    def __setitem__(self, key, value) :
        self._dic[key] = value
        
    def _get_local_mode(self) :		
        return self._local.items("global")[0][1]

    # Charge en mémoire des variables de configuration
    def get_vars(self) :
        # Chargement des valeurs par défaut
        for var in self._conf.items("global") :
            self._dic[var[0]] = _try_to_cast(var[1])
            
        # Si il y a un fichier local, on écrase les valeurs selon le mode.
        if not self._local is None :
            # On récupère le mode
            mode_local = self._get_local_mode()
            
            try : 
                for var in self._local.items(mode_local) :
                    self._dic[var[0]] = _try_to_cast(var[1])
            except configparser.NoSectionError :
                raise Exception("PAS DE SECTION ["+mode_local+"] dans /pc/config/local.ini !")
            
		    
        
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
        
