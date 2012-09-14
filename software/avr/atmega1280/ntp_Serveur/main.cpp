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
uint32_t t1;
uint32_t tp;
uint32_t t4;
uint32_t teta;
    
    
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
	
	//Ping du deuxieme avr
	if( strcmp(buffer, "??") == 0 )
	{
	    Serial<0>::print("Ping du second arduino");
	    Serial<1>::print_noln("?");
	    Serial<1>::read(buffer);
	    if( strcmp(buffer, "!") == 0 )
	    {
		Serial<0>::print("Ping arduino 2 réussi");
	    }
	}
	
	
	
	//Demande de synchronisation
	if( strcmp(buffer, "a") == 0 )
	{
		Serial<0>::print("Test de Synchronisation");
		synchronisation();
	}
	
	//Recuperation de l'horloge
	if( strcmp(buffer, "t") == 0 )
	{
		Serial<0>::print(clock);
	}
	
	//Recuperation des 2 horloges
	if( strcmp(buffer, "tt") == 0 )
	{
		Serial<0>::print("Timers local et distant:");
		Serial<1>::print_noln("t");
		Serial<1>::read(buffer);
		Serial<0>::print(clock);
		Serial<0>::print(buffer);
	}
	
	//Recuperation des 2 horloges en ms
	if( strcmp(buffer, "mm") == 0 )
	{
		float r;
		float t;
		Serial<0>::print("Timers local et distant:");
		Serial<1>::print_noln("t");
		Serial<1>::read(t);
		r = clock / 64.0;
		Serial<0>::print(r);
		r = t / 64.0;
		Serial<0>::print(r);
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

void synchronisation()
{
    //Declaration des variables
    char buffer[17];
    
    
    // Prépare le Client à effectuer une synchronisation
    Serial<0>::print("Tentative de synchro...");
    t1 = clock;
    Serial<1>::print_noln("!");
    Serial<1>::read(buffer);
    t4 = clock;
    
    if(strcmp(buffer, "!") == 0)
    {
	//Recuperation de la valeur de t2'
	Serial<1>::print_noln("tp?");
	Serial<1>::read(tp);

	
	//Calcul de l'écart teta entre les deux horloges
	teta = tp - (t1 + t4)/2;
	
	clock = clock + teta;
	
	Serial<0>::print("Synchro réussie");
	Serial<0>::print(t1);
	Serial<0>::print(tp);
	Serial<0>::print(t4);
	Serial<0>::print("Fin");
    }
    else Serial<0>::print("Erreur: réponse incorrecte. Echec synchro.");

    
    
}


ISR(TIMER0_OVF_vect)
{
  clock++;
}