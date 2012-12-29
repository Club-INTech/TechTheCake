#include "actionneurs.h"

Actionneurs::Actionneurs()
{
	serie::init();
	serie::change_baudrate(9600);
	Timer0::init();
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
		pos = 46000;
		integrale = 0;
		i = 0;
	}
	else if (strcmp(ordre, "bas") == 0) // Aller en bas
	{
		pos = 0;
		integrale = 0;
		i = 0;
	}
}
