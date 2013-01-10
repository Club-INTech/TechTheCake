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
	else if (strcmp(ordre, "haut") == 0) // Hauteur d'un verre
	{
		ascenceur_avant.consigne(ASCENSEUR_HAUT);
	}
	else if (strcmp(ordre, "bas") == 0) // Aller en bas
	{	
		ascenceur_avant.consigne(ASCENSEUR_BAS);
	}
	else if (strcmp(ordre, "!") == 0) // Donne sur la série la valeur de la codeuse
	{
		serie::print(ascenceur_avant.codeuse());
	}
	else if (strcmp(ordre, "consigne") == 0) // Demander de rentrer une consigne
	{
		serie::print("valeur ? ");
		int32_t consigne;
		serie::read(consigne); // Donner une consigne particulière
		ascenceur_avant.consigne(consigne);
		serie::print(consigne);
	}
	else if (strcmp(ordre, "da") == 0) // Désasservir moteur avant
	{
		ascenceur_avant.desasservir();
	}
	else if (strcmp(ordre, "ra") == 0) // Résasservir moteur avant
	{
		ascenceur_avant.reasservir();
	}
}
