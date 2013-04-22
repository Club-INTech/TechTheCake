#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <util/delay.h>

#include "twi_slave_asserv.h"

int main( void ){
	
    _delay_ms(10);
    // Interruptions
    sei();
    
    
    // I2C
    TWI_Init();
    
    while(1) {
        TWI_Loop();
    }

    return 0;
    
}


// Interruption codeur 1
ISR (PCINT0_vect)
{
    codeuse1.interruption();
}
// Interruption codeur 2
ISR (PCINT2_vect)
{
    codeuse2.interruption();
}
