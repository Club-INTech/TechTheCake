#include <libintech/codeuse.hpp>
#include <libintech/register.hpp>
#include <avr/interrupt.h>
#include <serial/serial_0.hpp>
#include <serial/serial_0_interrupt.hpp>

typedef Codeuse< AVR_PORTB <PORTB5>,AVR_PORTB <PORTB4> > codeuse;

int main()
{
codeuse::init();
while(1){}
return 1;
}

ISR (PCINT2_vect)
{
		
}