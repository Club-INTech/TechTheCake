#ifndef CAPTEUR_SRF05_HPP
#define CAPTEUR_SRF05_HPP

// Librairie standard :
#include <stdint.h>
#include <avr/io.h>
#include <util/delay.h>

// Librairie INTech :: Timer
#include <libintech/timer.hpp>

// Librairie INTech de manipulation de bits
#include <libintech/utils.h>

// Librarie INTech permettant l'utilisation simplifiée des ports et pin
#include <libintech/register.hpp>


/** @file libintech/capteur_srf05.hpp
 *  @brief Ce fichier crée une classe capteur_srf05 pour pouvoir utiliser simplement les capteurs SRF05.
 *  @author Thibaut ~MissFrance~
 *  @date 05 mai 2012
 */ 


/** @class capteur_srf05
 *  \brief Classe pour pouvoir gérer facilement les capteurs srf05.
 * 
 *  \param Timer               L'instance de Timer utilisé pour le calcul de distance.
 *  \param PinRegister         L'instance de registre
 * 
 *  La classe gère la récupération d'une distance entre le capteur et un obstacle.
 *  
 *  Protocole de ces capteurs :
 *  ---------------------------
 *
 *  La carte envoie une impulsion sur la pin pendant une durée de ~10µs. Puis, après
 *  une durée inconnue, le capteur envoie une impulsion sur cette même pin. La durée
 *  de cette impulsion est proportionnelle à la distance entre les capteurs et l'objet
 *  détecté.  
 */

template< class Timer, class PinRegisterIn, class PinRegisterOut >
class CapteurSRF
{
    uint16_t origineTimer;			//origine du timer afin de détecter une durée (le timer est une horloge)
    uint16_t derniereDistance;		//contient la dernière distance acquise, prête à être envoyée

   public:	//constructeur
   CapteurSRF() :
	derniereDistance(0)
    {
        PinRegisterOut::set_output();
        PinRegisterIn::set_input();
        PinRegisterOut::clear_interrupt();
        PinRegisterIn::set_interrupt();
    }

    uint16_t value()
    {
        return derniereDistance;
    }

    void refresh()
    {
            // On met un zéro sur la pin pour 2 µs
        PinRegisterOut::clear();
        _delay_us(2);

            // On met un "un" sur la pin pour 10 µs
        PinRegisterOut::set();
        _delay_us(10);

            // On remet un zéro puis on la met en input
        PinRegisterOut::clear();
    }
  
    /** Fonction appellée par l'interruption. S'occupe d'envoyer la valeur de la longueur
     *  de l'impulsion retournée par le capteur dans la série.
     */

    void interruption()
    {
        // Front montant si bit == 1, descendant sinon.
        uint8_t bit = PinRegisterIn::read();
        static uint8_t ancienBit=0;


        // Début de l'impulsion
        if (bit && bit!=ancienBit)
        {
            origineTimer=Timer::value();  /*le timer est utilisée comme horloge (afin d'utiliser plusieurs capteurs)
                                           On enregistre donc cette valeur et on fera la différence.*/
            ancienBit=bit;
        }

        // Fin de l'impulsion
        else if(!(bit) && bit!=ancienBit)
        {
            ancienBit=bit;
                //Enregistrement de la dernière distance calculée, mais pas envoyer (l'envoi se fait par la méthode value)
            derniereDistance=((Timer::value()+Timer::value_max()-origineTimer)&Timer::value_max())*(1700-0.0000325*F_CPU)/1800.;
                         /*interpolation linéaire entre deux valeurs
                         mesurées: 1050/1800 à 20MHz, 1180/1800 à 16MHz*/

        }
    }
};

#endif
