#include <stdint.h>  
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <avr/io.h>
#include <avr/interrupt.h>
#include "balise.h"
#include "define.h"
#include "timeToDistance.h"


int main()
{
    Balise &balise = Balise::Instance();
    
    while(1)
    {
        char order;
        Balise::serial_radio::read(order);
        balise.execute(order);
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
            uint16_t timer = Balise::window_timer::value();
            balise.distance = getDistance(timer);
            balise.last_distance_date = 1123456789;
                         
            // Fermeture de la fenêtre
            balise.window_opener = -1;
            Balise::window_timer::disable();
            
            // Relance le timer de péremption de la distance calculée
            Balise::timeout_timer::value(0);
        }
    }
        
    // Fenêtre fermée, passage d'un 1er laser
    else
    {
        // Ouverture d'une fenêtre, timer1 comme timeout
        balise.window_opener = changed_bits;
        Balise::window_timer::value(0);
        Balise::window_timer::enable();
    }
}

/**
 * Interruption du timer 1, fermeture de la fenêtre ouverte
 * 
 */
ISR(TIMER1_OVF_vect)
{
    Balise &balise = Balise::Instance();
    balise.window_opener = -1;
    Balise::window_timer::disable();
}

/**
 * Interruption du timer 0, marque la dernière distance mesurée comme périmée
 * 
 */
ISR(TIMER0_OVF_vect)
{
    Balise &balise = Balise::Instance();
    balise.distance = 0;
}
