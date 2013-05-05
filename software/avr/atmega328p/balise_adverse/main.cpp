#include <stdint.h>  
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/xbee.hpp>
#include <avr/io.h>
#include <avr/interrupt.h>
#include "balise.h"
#include "define.h"


int main()
{
    Balise &balise = Balise::Instance();
    
    while(1)
    {
        //~ char order[10];
        //~ Balise::xbee::read(order);
        //~ balise.execute(order);
        Balise::xbee::send(0x5001, "?");
    }
}

/**
 * Interruption lancée par le passage des lasers pour les PCINT8,9,10,11
 * 
 */
ISR(PCINT1_vect)
{
    Balise &balise = Balise::Instance();
    
    // Sauvegarde PINC pour savoir quelles pins ont changé
    static uint8_t port_c_history = 0xFF;
    uint8_t changed_bits = PINC ^ port_c_history;
    port_c_history = PINC;
    
    // Interruption sur front montant uniquement
    if ((PINC & changed_bits) == 0) return;

    // Fenêtre encore active, passage d'un 2ème laser
    if (balise.window_opener != -1)
    {
        // Ignore les doublets trop proches
        if (Balise::window_timer::value() * 20 >= TIME_THRESHOLD_MIN && changed_bits == balise.window_opener)
        {
            balise.distance = Balise::window_timer::value();
            
            // Déclenche le timer d'offset pour la mesure
            Balise::offset_timer::value(0);
            Balise::offset_timer::enable();
             
            // Fermeture de la fenêtre
            balise.window_opener = -1;
            Balise::window_timer::disable();
            
            // Allumage de la diode rouge
            balise.diode_blink(1, 15);		
        }
    }
        
    // Fenêtre fermée, passage d'un 1er laser
    else
    {
        // Ouverture d'une fenêtre
        balise.window_opener = changed_bits;
        Balise::window_timer::value(0);
        Balise::window_timer::enable();
    }
}

/**
 * Interruption du timer 2, fermeture de la fenêtre ouverte
 * 
 */
ISR(TIMER2_OVF_vect)
{
    Balise &balise = Balise::Instance();
    balise.window_opener = -1;
    Balise::window_timer::disable();
}

/**
 * Interruption du timer 1, marque la dernière distance mesurée comme périmée
 * 
 */
ISR(TIMER1_OVF_vect)
{
    Balise &balise = Balise::Instance();
    balise.distance = 0;
    Balise::offset_timer::disable();
    Balise::offset_timer::value(0);
}

/**
 * Interruption du timer 0, pour l'extinction de la diode debug
 * 
 */
ISR(TIMER0_OVF_vect)
{
	static bool status = false;
	static uint8_t modulo = 0;
	Balise &balise = Balise::Instance();
	
	modulo++;
	
    if (modulo < balise.blink_delay) return;
    
	if (status) {
		status = false;
		balise.diode_off();
		balise.blink_count--;
	}
	else {
		status = true;
		balise.diode_on();
	}
	
	if (balise.blink_count <= 0) {
		status = false;
		balise.diode_off();
		Balise::diode_timer::disable();
		Balise::diode_timer::value(0);
	}
	
	modulo = 0;
}
