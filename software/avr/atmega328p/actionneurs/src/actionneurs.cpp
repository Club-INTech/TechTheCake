#include "actionneurs.h"

Actionneurs::Actionneurs()
{
	serie::init();
	serie::change_baudrate(9600);
	timer_asserv::init();
	sei();
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
		ascenseur_avant.consigne(ASCENSEUR_HAUT);
	}
	else if (strcmp(ordre, "bas") == 0) // Aller en bas
	{	
		ascenseur_avant.consigne(ASCENSEUR_BAS);
	}
	else if (strcmp(ordre, "!") == 0) // Donne sur la série la valeur de la codeuse
	{
		serie::print(ascenseur_avant.codeuse());
	}
	else if (strcmp(ordre, "consigne") == 0) // Demander de rentrer une consigne
	{
		int32_t consigne;
		serie::read(consigne); // Donner une consigne particulière
		serie::print("_");
		ascenseur_avant.consigne(consigne);
	}
	else if (strcmp(ordre, "da") == 0) // Désasservir moteur avant
	{
		ascenseur_avant.desasservir();
	}
	else if (strcmp(ordre, "ra") == 0) // Résasservir moteur avant
	{
		ascenseur_avant.reasservir();
	}
	else if (strcmp(ordre, "changerConstantes") == 0)
	{
		int8_t pwm;
		float kp;
		float kd;
		float ki;
		serie::read(pwm);
		serie::print("_");
		serie::read(kp);
		serie::print("_");
		serie::read(kd);
		serie::print("_");
		serie::read(ki);
		serie::print("_");
		ascenseur_avant.modifierVitesseKpKdKi(pwm, kp, kd, ki);

	}
}
