#include "actionneurs.h"

Actionneurs::Actionneurs()
{
	serie::init();
	serie::change_baudrate(9600);
	timer_asserv::init();
	sei();
	TWI_init();
	serie::activer_acquittement(true);
}

void Actionneurs::communiquer(char *ordre)
{
	if (strcmp(ordre, "?") == 0)
	{
		serie::print("2");
	}
	if (strcmp(ordre, "h") == 0) // Hauteur d'un verre
	{
		ascenseur_arriere.consigne(ASCENSEUR_HAUT);
	}
	else if (strcmp(ordre, "b") == 0) // Aller en bas
	{	
		ascenseur_arriere.consigne(ASCENSEUR_BAS);
	}
	else if (strcmp(ordre, "m") == 0) // Aller en bas
	{	
		ascenseur_arriere.consigne(ASCENSEUR_4_VERRES);
	}
	else if (strcmp(ordre, "consigne") == 0) // Rentrer une consigne
	{
		int32_t consigne;
		serie::read(consigne); // Donner une consigne particulière
		ascenseur_arriere.consigne(consigne);
	}
	else if (strcmp(ordre, "c") == 0)
	{
		float kp;
		float kd;
		serie::read(kp);
		serie::read(kd);
		ascenseur_arriere.modifierVitesseKpKdKi(150, kp, kd, 0);

	}
	else if (strcmp(ordre, "!") == 0)
	{
		serie::print(ascenseur_arriere.valeurCodeuse());
	}
	else if (strcmp(ordre, "asc_av") == 0)
	{
		serie::read(ordre);
		if (strcmp(ordre, "haut") == 0) // Hauteur d'un verre
		{
			ascenseur_avant.consigne(ASCENSEUR_HAUT);
		}
		else if (strcmp(ordre, "bas") == 0) // Aller en bas
		{	
			ascenseur_avant.consigne(ASCENSEUR_BAS);
		}
		else if (strcmp(ordre, "plein") == 0) // Pour 4 verres
		{	
			ascenseur_avant.consigne(ASCENSEUR_4_VERRES);
		}
		else if (strcmp(ordre, "consigne") == 0) // Rentrer une consigne
		{
			int32_t consigne;
			serie::read(consigne); // Donner une consigne particulière
			ascenseur_avant.consigne(consigne);
		}
		else if (strcmp(ordre, "changerConstantes") == 0)
		{
			uint8_t bridage;
			float kp;
			float kd;
			float ki;
			serie::read(bridage);
			serie::read(kp);
			serie::read(kd);
			serie::read(ki);
			ascenseur_avant.modifierVitesseKpKdKi(bridage, kp, kd, ki);

		}
		else if (strcmp(ordre, "!") == 0)
		{
			serie::print(ascenseur_avant.valeurCodeuse());
		}
	}
	else if (strcmp(ordre, "asc_ar") == 0)
	{
		serie::read(ordre);
		if (strcmp(ordre, "haut") == 0) // Hauteur d'un verre
		{
			ascenseur_arriere.consigne(ASCENSEUR_HAUT);
		}
		else if (strcmp(ordre, "bas") == 0) // Aller en bas
		{	
			ascenseur_arriere.consigne(ASCENSEUR_BAS);
		}
		else if (strcmp(ordre, "plein") == 0) // Pour 4 verres
		{	
			ascenseur_avant.consigne(ASCENSEUR_4_VERRES);
		}
		else if (strcmp(ordre, "consigne") == 0) // Rentrer une consigne
		{
			int32_t consigne;
			serie::read(consigne); // Donner une consigne particulière
			ascenseur_arriere.consigne(consigne);
		}
		else if (strcmp(ordre, "changerConstantes") == 0)
		{
			uint8_t bridage;
			float kp;
			float kd;
			float ki;
			serie::read(bridage);
			serie::read(kp);
			serie::read(kd);
			serie::read(ki);
			ascenseur_arriere.modifierVitesseKpKdKi(bridage, kp, kd, ki);

		}
		else if (strcmp(ordre, "!") == 0)
		{
			serie::print(ascenseur_arriere.valeurCodeuse());
		}
	}
}
