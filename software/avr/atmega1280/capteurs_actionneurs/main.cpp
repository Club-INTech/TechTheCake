#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_1_interrupt.hpp>
#include <libintech/serial/serial_1.hpp>

#include "communications.h"

    Communications communications;

int main() 
{
    while(1)
    {
		char buffer[20];
        Communications::serie_robot::read(buffer);
        communications.execute(buffer);
    }
	return 0;
}

/**
 * Placer ici les interruptions, minimiser le code (appels aux méthodes du singleton actionneurs)
 * 
 */
ISR (TIMER1_OVF_vect)
{

}

ISR (PCINT2_vect)
{
}

ISR(TIMER0_OVF_vect)
{
}

ISR(TIMER2_OVF_vect) //overflow du timer 2, qui appelle le refresh d'un ou des capteur(s) SRF05 (autant de refresh que de capteurs)
{
    static uint8_t overflow=0;  //on appelle la fonction refresh qu'une fois sur 5 overflow
    if(overflow==0)
    {
        communications.capteurs.us1.refresh();
        communications.capteurs.us2.refresh();
        communications.capteurs.inf1.refresh();
        communications.capteurs.inf2.refresh();
    }
    overflow++;
    overflow%=5;
}

ISR(PCINT0_vect)
{
    communications.capteurs.us1.interruption();
    communications.capteurs.us2.interruption();
}

