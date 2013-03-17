#ifndef BALISE_H
#define BALISE_H

#include <stdint.h>
#include <libintech/singleton.hpp>
#include <libintech/moteur.hpp>
#include <libintech/asservissement.hpp>
#include <libintech/timer.hpp>
#include <util/delay.h>
#include "define.h"

#if MODE_XBEE_S8 == 1
#include <libintech/xbees8.hpp>
#else
#include <libintech/xbee.hpp>
#endif

class Balise : public Singleton<Balise>
{
    public:
        #if MODE_XBEE_S8 == 1
        typedef XbeeS8< Serial<0> > xbee;
        #else
        typedef Xbee< Serial<0> > xbee;
        #endif
        
        /**
         * Timer utilisé pour calculer l'écart de temps entre les 2 lasers
         * Fermeture de la fenêtre quand il overflow
         */
        typedef Timer<2,128> window_timer;
        
        /**
         * Timer utilisé pour mesurer l'offset de temps pour la mesure
         * Mise à zero de la mesure quand il overflow
         */
        typedef Timer<1,64> offset_timer;
        
        /**
         * Timer utilisé pour controler le clignotage des diodes
         */
        typedef Timer<0,64> diode_timer;
        
        /**
         * Indique par qui une fenêtre de passage des lasers a été ouverte
         * -1 = fenêtre fermée
         */
        volatile int8_t window_opener;
        
        /**
         * Dernière distance mesurée
         */
        volatile uint16_t distance;
        
        /**
         * Nombre de clignotement de la diode restant à effectuer
         */
        volatile uint8_t blink_count;
        
        /**
         * Prescaler pour le clignotement de la diode
         */
        volatile uint8_t blink_delay;
        
    public:
        Balise();
        void execute(char*);
        void diode_on();
        void diode_off();
        void diode_blink(uint8_t, uint8_t);
        
    private:
        uint32_t format_value(uint16_t, uint16_t);
    
    private:
		
};

#endif
