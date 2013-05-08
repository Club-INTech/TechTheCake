#ifndef CAPTEURS_ROBOT_SECONDAIRE_H
#define CAPTEURS_ROBOT_SECONDAIRE_H

#include <libintech/capteur_infrarouge.hpp>
#include <libintech/capteur_srf05.hpp>

#define NB_SRF_AVANT            1
#define NB_INFRAROUGE_AVANT     1

#define TAILLE_BUFFER_ASC   50

/**
 * Gestion des actionneurs
 * 
 */
class Capteurs
{
	public:
            //Le prescalaire 64 est nécessaire (sinon les valeurs retournées sont fausses)
        typedef Timer<1, 64> timer_capteur_us;
        typedef Timer<0, 1024> timer_refresh;
        
        typedef CapteurSRFMono< timer_capteur_us, AVR_PORTD<PORTD5> > us_robot;
		us_robot us;

        typedef CapteurInfrarouge< AVR_ADC<0> > ir_robot;
		ir_robot ir;
	public:
		Capteurs();
};

#endif
