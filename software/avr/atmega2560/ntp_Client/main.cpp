// LIBRAIRIES STANDARD
#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// LIBRAIRIE INTECH
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

// LIBRAIRIES LOCALES


/********************************
 *           CONSTANTES         *
 ********************************/

#define BAUD_RATE_SERIE         9600
#define COMPARE_BUFFER(string,len) strncmp(buffer, string, len) == 0 && len>0

/******************************** 
 *   MODES DE CONFIGURATION     *   
 ********************************/

void setup();


typedef Serial<0> serial_t_;

int main()
{
    // Initialisation de la liaison série PC <-> Carte.
    setup();

    
    while (1)
        
    {

	char buffer[17];
	Serial<0>::read(buffer,17);

	
	//Ping
	if(COMPARE_BUFFER("?",1))
	{
		Serial<0>::print("Hello World !x");
	}
	
	
    }
    return 0;
}

void setup()
{
  
        sei();

	//Initialisation série
	Serial<0>::init();
	Serial<0>::change_baudrate(9600);

}

