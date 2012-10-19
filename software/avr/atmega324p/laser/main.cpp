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
    
    balise.diode_blink();
    
    while(1)
    {
        char buffer[20];
        Balise::serial_pc::read(buffer);
        balise.execute(buffer);
    }
}


ISR(TIMER0_OVF_vect)
{
    Balise &balise = Balise::Instance();
    balise.synchro.interruption();
}

ISR(TIMER2_OVF_vect)
{
    //Serial<0>::print(codeur - last_codeur);
    //  Balise::Instance().asservir(codeur - last_codeur);
    //  last_codeur = codeur;
}

// Overflow timer top-tour
ISR(TIMER1_OVF_vect)
{
    Balise &balise = Balise::Instance();
    
    // Remise à zéro de la vitesse
    balise.max_counter(0);

    // Désactivation du timer
    Balise::timer_toptour::disable();
    Balise::timer_toptour::value(0);
}

// Interruption top-tour
ISR(INT2_vect)
{
    Balise &balise = Balise::Instance();
    
    Balise::timer_toptour::enable();
    
    // On ignore les impulsions quand l'aimant est encore trop proche du capteur
    if (Balise::timer_toptour::value() >= balise.max_counter() / 3)
    {
        balise.max_counter(Balise::timer_toptour::value());
        Balise::timer_toptour::value(0);
    }
}

ISR(PCINT0_vect)
{
//   if(dernier_etat_a == 0 && READ_CANAL_A() == 1){
//     if(READ_CANAL_B() == 0)
//       codeur--;
//     else
//       codeur++;
//   }
//   else if(dernier_etat_a == 1 && READ_CANAL_A() == 0){
//     if(READ_CANAL_B() == 0)
//       codeur++;
//     else
//       codeur--;
//   }
//   else if(dernier_etat_b == 0 && READ_CANAL_B() == 1){
//     if(READ_CANAL_A() == 0)
//       codeur--;
//     else
//       codeur++;
//   }
//   else if(dernier_etat_b == 1 && READ_CANAL_B() == 0){
//     if(READ_CANAL_A() == 0)
//       codeur++;
//     else
//       codeur--;
//   }
//  dernier_etat_a = READ_CANAL_A();
//  dernier_etat_b = READ_CANAL_B(); 
}
