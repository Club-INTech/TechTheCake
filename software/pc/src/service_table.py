#1  code ABSOLUMENT avec kate pour éviter les erreur d'indentation
#   je l'ai configuré pour que <tab>  indente de 4 espaces, et <maj>+<tab> désindente

#2 passe le code en objet, dans une belle classe Table
#une variable [cadeaux = ] devient un attribut de classe [self.cadeaux = ]
#tu appelles un attribut comme ca : [self.cadeaux[id]]
#une fonction [def fonction (parametre1, parametre2):] devient une méthode [def fonction (self,parametre1, parametre2):]
#tu appelles une méthode comme ca : [self.fonction(param1,param2)]

class Table:

    def __init__(self):
        #c'est le constructeur...je te montre ca après
        pass
        
        
        
    	

# On prend pour origine l'angle inférieur de la table correspondant à notre bord de départ.
cadeaux = [	
	{"position":(525,0),"ouvert":False},
	{"position":(1125,0),"ouvert":False},
	{"position":(1725,0),"ouvert":False},
	{"position":(2325,0),"ouvert":False}]

# La position des bougies est codée en pôlaire depuis le centre du gâteau : ( rayon, angle depuis l'horizontale ), elles sont ordonnées par ordre croissant d'angle.
bougies = [
	{"position":(450,7.5), "traitee":False, "enHaut":False},
	{"position":(350,11.25), "traitee":False, "enHaut":True},
	{"position":(450,22.5), "traitee":False, "enHaut":False},
	{"position":(350,33.75), "traitee":False, "enHaut":True},
	{"position":(450,37.5), "traitee":False, "enHaut":False},
	{"position":(450,52.5), "traitee":False, "enHaut":False},
	{"position":(350,56.25), "traitee":False, "enHaut":True},
	{"position":(450,67.5), "traitee":False, "enHaut":False},
	{"position":(350,78.75), "traitee":False, "enHaut":True},
	{"position":(450,82.5), "traitee":False, "enHaut":False},
	{"position":(450,97.5), "traitee":False, "enHaut":False},
	{"position":(350,101.25), "traitee":False, "enHaut":True},
	{"position":(450,112.5), "traitee":False, "enHaut":False},
	{"position":(350,123.75), "traitee":False, "enHaut":True},
	{"position":(450,127.5), "traitee":False, "enHaut":False},
	{"position":(450,142.5), "traitee":False, "enHaut":False},
	{"position":(350,146.25), "traitee":False, "enHaut":True},
	{"position":(450,157.5), "traitee":False, "enHaut":False},
	{"position":(350,168.75), "traitee":False, "enHaut":True},
	{"position":(450,172.5), "traitee":False, "enHaut":False}]

# Le premier correspond à celui le plus en haut à gauche et le dernier le plus en bas à droite.
verres = [
	{"id" : 0, "position":(900,1050), "present":True},
	{"id" : 1, "position":(1200,1050), "present":True},
	{"id" : 2, "position":(1800,1050), "present":True},
	{"id" : 3, "position":(2100,1050), "present":True},
	{"id" : 4, "position":(1050,800), "present":True},
	{"id" : 5, "position":(1350,800), "present":True},
	{"id" : 6, "position":(1650,800), "present":True},
	{"id" : 7, "position":(1950,800), "present":True},
	{"id" : 8, "position":(900,550), "present":True},
	{"id" : 9, "position":(1200,550), "present":True},
	{"id" : 10, "position":(1800,550), "present":True},
	{"id" : 11, "position":(2100,550), "present":True}]

# A utiliser lorsqu'un cadeau est tombé.
def cadeau_recupere( pos ) :
	cadeaux[pos]["ouvert"]=True
	
# Permet de savoir l'état d'un cadeau.	
def etat_cadeau( pos ) :
	return cadeaux[pos]["ouvert"]
	
# A utiliser lorsqu'une bougie est tombée.
def bougies_recupere( pos ) :
	bougies[pos]["traitee"]=True
	
# Permet de savoir l'état d'une bougie.
def etat_bougie( pos ) :
	return bougies[pos]["traitee"]
	
# A utiliser lorsqu'un verre est déjà utilisé.
def verre_recupere( pos ) :
	verres[pos]["present"]=False
	
# Permet de savoir l'état d'un verre.
def etat_verre( pos ) :
	return verres[pos]["present"]
	
	
