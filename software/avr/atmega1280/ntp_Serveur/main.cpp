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


typedef Timer<1,ModeCounter,256> clock;

void setup();
void synchronisation();

int main()
{
    // Initialisation de la liaison série PC <-> Carte.
    setup();

    
    while (1)
        
    {
	char buffer[17];
	Serial<0>::read(buffer);

	
	//Ping
	if( strcmp(buffer, "?") == 0 )
	{
		Serial<0>::print("Hello World!");
	}
	
	//Demande de synchronisation
	if( strcmp(buffer, "a") == 0 )
	{
		Serial<0>::print("Test de Synchronisation");
		synchronisation();
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
	clock::init();

}

void synchronisation()
{
    char buffer1[17];
    Serial<0>::print("Tentative de ping...");
    Serial<1>::print_noln("?");
    Serial<1>::read(buffer1);
    if(strcmp(buffer1, "!") == 0)
    {
	Serial<0>::print("ping succeed");
	Serial<1>::print_noln(clock::value());
	Serial<1>::read(buffer1);
	Serial<0>::print(buffer1);
    }
    else Serial<0>::print("Erreur, réponse incorrecte!");
    
}


ISR(TIMER1_OVF_vect)
{
	//Rien
}