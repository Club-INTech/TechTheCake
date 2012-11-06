
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
typedef capteur_srf05< timerCapteurSRF, serial_t_ > capteur_srf05_t_;

int main()
{
    // Initialisations de tous les objets.
    capteur_infrarouge  ::init();
    capteur_srf05_t_    ::init();
    serial_t_           ::init();
    
    // Changement du BAUD RATE de la série carte <-> PC
    serial_t_::change_baudrate(BAUD_RATE_SERIE);

    // Activation de toutes les interruptions (notamment les interruptions
    // de la liaison série carte <-> carte).
    sei();
    
    while (1)
    {
        /// ******************************************
        /// **          PROGRAMME PRINCIPAL         **
        /// ******************************************
        //serial_t_::print(0);
        char buffer[17];
        serial_t_::read(buffer);
        
        
        
        /// *********************************************** ///
        ///                 CAPTEURS                        ///
        /// *********************************************** ///
        
        
        // infrarouge
        if (strcmp(buffer, "i")==0)
            serial_t_::print(capteur_infrarouge::value());
        
        else if (strcmp(buffer, "u")==0)
            serial_t_::print(capteur_infrarouge::value_brut());
        
        // Ultrasons SRF05
        else if (strcmp(buffer, "s")==0)
            capteur_srf05_t_::value();
            // C'est une interruption qui s'occupe d'afficher
            // la valeur.*/
    }
    return 0;
}


// Overflow du timer 1 (utilisé notamment par les ultrasons SRF05
ISR(TIMER1_OVF_vect){
    capteur_srf05_t_::timerOverflow();
}
