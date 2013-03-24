#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <libintech/codeuse.hpp>

#include "twi_slave.h"

typedef Codeuse<AVR_PORTD <PORTD2>, AVR_PORTD <PORTD3> codeuseAvant;
typedef Codeuse<AVR_PORTD <PORTD4>, AVR_PORTD <PORTD5> codeuseArriere;
codeuseAvant codeuseMoteurAvant;
codeuseArriere codeuseMoteurArriere

int main( void ){

	// Interruptions
	sei();

	// I2C
	TWI_Init();

	// Compteur
	compteur_init();

	

	while(1) {
		TWI_Loop();
	}

	return 0;

}

ISR (PCINT2_vect)
{
	codeuseMoteurAvant.interruption();
	codeuseMoteurArriere.interruption();
}
