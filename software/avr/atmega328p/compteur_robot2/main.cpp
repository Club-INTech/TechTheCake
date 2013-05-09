#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>

#include "twi_slave_asserv2.h"

void setup();
static int8_t mb1 = 0;
static int8_t mb2 = 0;

int main( void ){
	
    _delay_ms(100);
    // Interruptions
    sei();
    
	setup();
    
    // I2C
    TWI_Init();
    
    while(1) {
        TWI_Loop();
    }

    return 0;
    
}


// Interruption codeur 1
ISR (INT0_vect)
{
	if(mb1) --codeuse1;
	else ++codeuse1;

	mb1 = rbi(PINC,PINC0);
}

// Interruption codeur 2
ISR (INT1_vect)
{
	if(mb2) ++codeuse2;
	else --codeuse2;

	mb2 = rbi(PINC,PINC1);
}


void setup()
{
/**
 * Activer en lecture les 4 pins
 * Activer les interr INT0/1 sur front montant
 **/
	//Activation des interruptions externes
	sbi(EIMSK,INT0);
	sbi(EIMSK,INT1);

	//Activation des interruptions sur fronts montants
	//INT0
	sbi(EICRA,ISC01);
	sbi(EICRA,ISC00);
	//INT1
	sbi(EICRA,ISC11);
	sbi(EICRA,ISC10);

	//Pins en lecture des pins
	cbi(DDRD,DDD2); // Signal A moteur Gauche
	cbi(DDRD,DDD3); // Signal A moteur Droit
	cbi(DDRC,DDC0); // Signal B moteur Gauche
	cbi(DDRC,DDC1); // Signal B moteur Droit
}
