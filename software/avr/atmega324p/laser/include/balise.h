#ifndef BALISE_H
#define BALISE_H

#include <stdint.h>
#include <libintech/singleton.hpp>
#include <libintech/timer.hpp>
#include <libintech/pwm.hpp>
#include <libintech/moteur.hpp>
#include <libintech/asservissement.hpp>
#include <libintech/register.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_1.hpp>
#include <libintech/ring_buffer.hpp>
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
    
		/**
		 * Communication vers le PC
		 */
        typedef Serial<0> serial_pc;
        
        /**
         * Communication radio
         */
        #if MODE_XBEE_S8 == 1
        typedef XbeeS8< Serial<1> > xbee;
        #else
        typedef Xbee< Serial<1> > xbee;
        #endif
        
        /**
         * Timer utilisé pour calculer l'angle des lasers
         *
         * Doit être le plus précis possible (16 bits), mais ne doit pas faire d'overflow
         */
        typedef Timer<1,64> timer_toptour;
        
        /**
         * Moteur sur le Timer 0 en FastPWM. Pont en H sur le PORTB3
         */
        typedef PWM<0,ModeFastPwm,1,'A'> pwm_motor;
        
        /**
         * PWM Laser
         * 
         * Prescaler 1: f = 80kHZ (fait chauffer le pont de diodes)
         * Prescaler 8: f = 10kHz (bruyant)
         */
        typedef PWM<0,ModeFastPwm,1,'B'> pwm_laser;
        
        /**
         * Moteur
         */
        Moteur< pwm_motor, AVR_PORTD<PORTD4> > motor;
        
        /**
         * Asservissement du moteur
         */
        Asservissement motor_control;

        /**
         * Timer pour la boucle d'asservissement
         */
        typedef Timer<2,1024> timer_control;
        
        /**
         * Valeur de la codeuse
         */
        volatile int32_t encoder;
        
    private:
        volatile uint16_t last_period_;
        volatile int16_t pwm_;
        
        
    public:
        Balise();
        void execute(char*);
        void last_period(uint16_t);
        uint16_t last_period();
        float angle(int32_t);
        void motor_on();
        void motor_off();
        void control(int32_t);
        void laser_on();
        void laser_off();
        void diode_on();
        void diode_off();
        void diode_blink();
        void diode_blink(uint16_t, uint8_t);
};

#endif
