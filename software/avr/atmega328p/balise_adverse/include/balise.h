#ifndef BALISE_H
#define BALISE_H

#include <stdint.h>
#include <libintech/singleton.hpp>
#include <libintech/moteur.hpp>
#include <libintech/asservissement.hpp>
#include <libintech/register.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/xbee.hpp>
#include <libintech/timer.hpp>
#include <util/delay.h>
#include "define.h"
#include <lib2013/synchronisation.hpp>

class Balise : public Singleton<Balise>
{
    public:
        typedef Xbee< Serial<0> > xbee;
        
        /**
         * Timer utilisé comme timeout pour marquer la distance mesurée comme périmée au bout d'un certain temps
         */
        typedef Timer<0,1024> timeout_timer;
        
        /**
         * Timer utilisé pour mesurer le temps de passage des lasers
         * Sert également de timeout, fermeture de la fenêtre quand il overflow
         */
        typedef Timer<1,64> window_timer;
        
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
         * Date de la dernière distance mesurée
         */
        volatile uint32_t last_distance_date;
        
        Synchronisation< Timer<2,1> , Xbee<Serial<0> > > synchronisation;
        
    public:
        Balise();
        void execute(char*);
        void diode_on();
        void diode_off();
        void diode_blink();
        void diode_blink(uint16_t, uint8_t);
        
    private:
        uint32_t format_value(uint16_t, uint16_t);
};

#endif
