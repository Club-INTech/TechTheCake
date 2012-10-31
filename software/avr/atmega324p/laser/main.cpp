#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_1_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_1.hpp>
#include <libintech/timer.hpp>
#include <stdint.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include "balise.h"

int main() 
{
    Balise &balise = Balise::Instance();
    
    while(1)
    {
        char buffer[20];
        Balise::serial_pc::read(buffer);
        balise.execute(buffer);
    }
}


ISR(TIMER0_OVF_vect)
{

}

ISR(TIMER2_OVF_vect)
{
	static int32_t last_codeur = 0;
	Balise &balise = Balise::Instance();
    Balise::Instance().asservir(balise.codeur - last_codeur);
    last_codeur = balise.codeur;
}

/**
 * Interruption timer top tour
 * 
 */
ISR(TIMER1_OVF_vect)
{
	Balise &balise = Balise::Instance();
		
    // Remise à zéro de la vitesse	
    balise.last_period(0);
		
    // Désactivation du timer	
    Balise::timer_toptour::disable();	
    Balise::timer_toptour::value(0);
}

/**
 * Interruption capteur top tour (aimant passant devant le capteur)
 * 
 */
ISR(INT2_vect)
{
    Balise &balise = Balise::Instance();
    
    // On ignore les impulsions quand l'aimant est encore trop proche du capteur
    if (Balise::timer_toptour::value() >= balise.last_period() / 3)
    {
        balise.last_period(Balise::timer_toptour::value());
        Balise::timer_toptour::value(0);
        Balise::timer_toptour::enable();	
    }
}


ISR(PCINT2_vect)
{
	static uint8_t canal_a;
	static uint8_t canal_b;
	static uint8_t previous_canal_a;
	static uint8_t previous_canal_b;
	
	Balise &balise = Balise::Instance();
	
	canal_a = rbi(PINC,PORTC1);
	canal_b = rbi(PINC,PORTC0);
	
	// Vérification que l'on est sur un front (useless ?)
	if (!(canal_a != previous_canal_a || canal_b != previous_canal_b)) return;
	
	bool sens = canal_a == previous_canal_b;
	
	// Incrémente ou décrémente en fonction du sens
	if (sens)
	{
		balise.codeur++;
	}
	else
	{
		balise.codeur--;
	}
	
	previous_canal_a = canal_a;
	previous_canal_b = canal_b;
}

