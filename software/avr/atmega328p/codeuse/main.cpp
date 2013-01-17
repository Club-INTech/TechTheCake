#include <libintech/codeuse.hpp>
#include <libintech/register.hpp>
#include <avr/interrupt.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>


typedef Codeuse< AVR_PORTD <PORTD2>,AVR_PORTD <PORTD3> > codeuse;
typedef Serial<0> serialPC;
codeuse c;

int main()
{
	sei();
	serialPC::init();
	
	while(1)
	{
		serialPC::print(c.compteur());
	}
	return 0;
}

ISR (PCINT2_vect)
{
	c.interruption();
}