#include "actionneurs.h"

Actionneurs::Actionneurs()
{
	serie::init();
	serie::change_baudrate(9600);
	timer_asserv::init();
	sei();
	compteur_init();
		
}
void Actionneurs::execute(char *ordre)
{
	serie::print("_");
	
	if (strcmp(ordre, "?") == 0)
	{
		serie::print("2");
	}
	else if (strcmp(ordre, "haut") == 0) //Hauteur d'un verre
	{
		ascenceur_avant.consigne(ASCENSEUR_HAUT);
	}
	else if (strcmp(ordre, "bas") == 0) // Aller en bas
	{	
		ascenceur_avant.consigne(ASCENSEUR_BAS);
	}
}
