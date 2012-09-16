// LIBRAIRIES STANDARD
#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <libintech/timer.hpp>

// LIBRAIRIE INTECH
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_1_interrupt.hpp>
#include <libintech/serial/serial_1.hpp>


// LIBRAIRIES LOCALES


/********************************
 *           CONSTANTES         *
 ********************************/

#define BAUD_RATE_SERIE         9600

/******************************** 
 *   MODES DE CONFIGURATION     *   
 ********************************/


typedef Timer<0,ModeCounter,1> timer;
volatile uint32_t clock=0;

void setup();

uint32_t tp;

int main()
{
    // Initialisation de la liaison série PC <-> Carte.
    setup();

    
    while (1)
        
    {
	
	char buffer[17];
	
	Serial<1>::read(buffer);
	
	//demande de ping
	if( strcmp( buffer , "?" ) == 0 )
	{
	   Serial<1>::print("!");
	}
	
	//Demande de synchronisation
	if( strcmp( buffer , "!" ) == 0 )
	{
		//Memorisation de l'heure d'envoie et ping retour
		tp = clock;
		Serial<1>::print("!");
		
		// Attente de la demande de tp et envoie
		Serial<1>::read(buffer);
		if( strcmp( buffer , "tp?" ) == 0 ) Serial<1>::print_noln(tp);
	}
	
	//Demande d'horloge
	if( strcmp( buffer , "t" ) == 0 )
	{
	   Serial<1>::print(clock);
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
	Serial<1>::init();
	Serial<1>::change_baudrate(9600);
	
	//Timers
	timer::init();

}

ISR(TIMER0_OVF_vect)
{
  clock++;
}