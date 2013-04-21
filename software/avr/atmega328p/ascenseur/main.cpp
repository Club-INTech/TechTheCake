#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "actionneurs.h"
#include "twi_master.h"

int main() 
{
	Actionneurs &actionneurs = Actionneurs::Instance();

	while(1)
	{
		char buffer[20];
		Actionneurs::serie::read(buffer);
		actionneurs.communiquer(buffer);
	}
	return 0;
}

/**
 * Placer ici les interruptions, minimiser le code (appels aux méthodes du singleton actionneurs)
 * 
 */
ISR (TIMER1_OVF_vect, ISR_NOBLOCK)
{
	Actionneurs &actionneurs = Actionneurs::Instance();
	int32_t position[2];
	Actionneurs::timer_asserv::value(54000); // On met une valeur sur le timer d'asservissement  pour accéder plus rapidement au prochain overflow
	get_all(position);
	actionneurs.ascenseur_arriere.changerValeurCodeuse(position[0]);
	actionneurs.ascenseur_avant.changerValeurCodeuse(position[1]);
    
	actionneurs.ascenseur_arriere.asservir();
	actionneurs.ascenseur_avant.asservir();
}


ISR(TIMER0_OVF_vect)
{
}

ISR(TIMER2_OVF_vect)
{
}
