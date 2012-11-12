#include <libintech/utils.h>
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

int main()
{
    // Mode OUTPUT de la pin 5 du port B (pin 13 arduino).
    sbi(DDRB, DDB5);    

while(1)

{

// ON

sbi(PORTB, PORTB5);

_delay_ms(500);

// OFF

cbi(PORTB, PORTB5);       

_delay_ms(500);

}

return 0;
}
