#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>

#include "twi_slave.h"
#include "compteur.h"


int main( void ){
	
    _delay_ms(100);
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
