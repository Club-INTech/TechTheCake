#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <avr/io.h>
#include <stdint.h>  

int main() 
{
 	//Initialisation série
	Serial<0>::init();
	Serial<0>::change_baudrate(9600);
	sei();
	
	while(1){
		int32_t buf;
		Serial<0>::read(buf);
		Serial<0>::print(buf);
	}
	
	return 0;
}
