
/** @file avr/atmega324p/actionneurs/main.cpp
 *  @brief Ce fichier s'occupe de gérer l'AVR Capteur-actionneurs
 *  @author Thibaut ~MissFrance~
 *  @date 09 mai 2012
 */ 

// LIBRAIRIES STANDARD
#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// LIBRAIRIE INTECH :: Série
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

// LIBRAIRIE INTECH :: Capteurs
#include <libintech/capteur_infrarouge.hpp>
#include <libintech/capteur_srf05.hpp>


/********************************
 *           CONSTANTES         *
 ********************************/

#define BAUD_RATE_SERIE         9600


/** Ce fichier gère la carte qui fait le lien entre les AX12, les capteurs ultrasons,
 *  le jumper de début de match et la carte PCI.
 * 
 *  La série 1 est dédiée à la communication Carte  ->  AX12
 *  La série 0 est dédiée à la communication Carte <->   PC
 *  Le pin 7 est dédié au jumper.
 *  Le pin analog0 est dédiée aux infrarouges.
 */

// Liaison série Carte <-> PC
typedef Serial<0> serial_t_;

// Ultrasons SRF05
typedef Timer<1, 64> timerCapteurSRF;
typedef Timer<2, 1024> timerRefresh;
typedef CapteurSRF< timerCapteurSRF, AVR_PORTB<PORTB1>, AVR_PORTB<PORTB2> > srf1;
srf1 capteur_srf05_t_1;
typedef CapteurSRF< timerCapteurSRF, AVR_PORTB<PORTB3>, AVR_PORTB<PORTB4> > srf2;
srf2 capteur_srf05_t_2;

typedef CapteurInfrarouge< AVR_ADC<PORTC0> > cap_infra1;
cap_infra1 capteur_infrarouge_1;
typedef CapteurInfrarouge< AVR_ADC<PORTC1> > cap_infra2;
cap_infra2 capteur_infrarouge_2;

/* correspondances pin/port:
pin 0 <-> PORTD0
pin 1 <-> PORTD1
pin 2 <-> PORTD2
pin 3 <-> PORTD3
pin 4 <-> PORTD4
pin 5 <-> PORTD5
pin 6 <-> PORTD6
pin 7 <-> PORTD7
pin 8 <-> PORTB0
pin 9 <-> PORTB1
pin 10 <-> PORTB2
pin 11 <-> PORTB3
pin 12 <-> PORTB4
pin 13 <-> PORTB5 (à éviter! pin de debug uniquement)

analog in 0 <-> PORTC0
analog in 1 <-> PORTC1
analog in 2 <-> PORTC2
analog in 3 <-> PORTC3
analog in 4 <-> PORTC4
analog in 5 <-> PORTC5
*/

int main()
{
    // Initialisations de tous les objets.
    serial_t_           ::init();
    timerCapteurSRF     ::init();
    timerRefresh        ::init();

    // Changement du BAUD RATE de la série carte <-> PC
    serial_t_::change_baudrate(BAUD_RATE_SERIE);

    while (1)
    {
        /// ******************************************
        /// **          PROGRAMME PRINCIPAL         **
        /// ******************************************
        char buffer[17];
        serial_t_::read(buffer);
        
        
        
        /// *********************************************** ///
        ///                 CAPTEURS                        ///
        /// *********************************************** ///


        // infrarouge
        if (strcmp(buffer, "i")==0) //minuscule: arrière. Majuscule: avant
            serial_t_::print(capteur_infrarouge_1.value());

        else if (strcmp(buffer, "I")==0)
            serial_t_::print(capteur_infrarouge_2.value());

        else if (strcmp(buffer, "u")==0) //debug (valeur brute, à ne pas utiliser directement)
            serial_t_::print(capteur_infrarouge_1.value_brut());


        // Ultrasons SRF05
        else if (strcmp(buffer, "S")==0)
            serial_t_::print(capteur_srf05_t_1.value());

        else if (strcmp(buffer, "s")==0)
            serial_t_::print(capteur_srf05_t_2.value());

        //serial de la carte (ping)
        else if (strcmp(buffer, "?")==0)
            serial_t_::print(3);

    }
    return 0;
}

ISR(TIMER2_OVF_vect) //overflow du timer 2, qui appelle le refresh d'un ou des capteur(s) SRF05 (autant de refresh que de capteurs)
{
    static uint8_t overflow=0;  //on appelle la fonction refresh qu'une fois sur 5 overflow
    if(overflow==0)
    {
        capteur_srf05_t_1.refresh();
//        capteur_srf05_t_2.refresh();
        capteur_infrarouge_1.refresh();
    }
    overflow++;
    overflow%=5;
}
ISR(TIMER1_OVF_vect)    //MÊME SI ELLE EST VIDE, IL EST OBLIGATOIRE DE DEFINIR CETTE FONCTION
{}

ISR(PCINT0_vect)
{
   capteur_srf05_t_1.interruption();
//   capteur_srf05_t_2.interruption();
}

