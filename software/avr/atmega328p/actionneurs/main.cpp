#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

#include "actionneurs.h"

int main() 
{
	sei();
	Actionneurs &actionneurs = Actionneurs::Instance();
    
    while(1)
    {
		char buffer[20];
        Actionneurs::serie::read(buffer);
        actionneurs.execute(buffer);
    }
	return 0;
}

/**
 * Placer ici les interruptions, minimiser le code (appels aux méthodes du singleton actionneurs)
 * 
 */
ISR (TIMER1_OVF_vect)
{
	Actionneurs &actionneurs = Actionneurs::Instance();
	Actionneurs::timer_asserv::value(54000); // On met une valeur sur le timer d'asservissement  pour accéder plus rapidement au prochain overflow
	actionneurs.ascenseur_avant.asservir();
}

ISR (PCINT2_vect)
{
	Actionneurs &actionneurs = Actionneurs::Instance();
	actionneurs.ascenseur_avant.libcodeuse.interruption();
}

ISR(TIMER0_OVF_vect)
{
}

ISR(TIMER2_OVF_vect)
{
}
