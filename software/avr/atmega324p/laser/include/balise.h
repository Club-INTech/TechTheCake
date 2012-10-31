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
#include <libintech/xbee.hpp>
#include <util/delay.h>
#include "define.h"

class Balise : public Singleton<Balise>
{
    public:
    
		// Communication vers le PC
        typedef Serial<0> serial_pc;
        
        // Communication radio
        typedef Xbee< Serial<1> > xbee;
        
        /**
         * Timer utilisé pour calculer l'angle des lasers
         *
         * Doit être le plus précis possible (16 bits), mais ne doit pas faire d'overflow
         */
        typedef Timer<1,64> timer_toptour;
        
        /**
         * Moteur sur le Timer 0 en FastPWM. Pont en H sur le PORTB3
         */
        typedef PWM<0,ModeFastPwm,1,'A'> pwm_moteur;
        
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
        Moteur< pwm_moteur, AVR_PORTD<PORTD4> > moteur;
        
        /**
         * Asservissement du moteur
         */
        Asservissement asservissement_moteur;
        
        //typedef PWM<0,ModeCTC,1,'B'> pwm_laser;
        
        typedef Timer<2,1024> timer_asservissement;
        
        //Valeur de la codeuse du moteur
        volatile int32_t codeur;
        
    private:
        volatile uint16_t last_period_;
        volatile int16_t pwm_;
        
        
    public:
        Balise();
        void execute(char*);
		void asservir(int32_t);
        void last_period(uint16_t);
        uint16_t last_period();
        float angle(int32_t);
        void motor_on();
        void motor_off();
        void laser_on();
        void laser_off();
        void diode_on();
        void diode_off();
        void diode_blink();
        void diode_blink(uint16_t, uint8_t);
        
    private:
        uint32_t format_value(uint16_t, uint16_t);
};

#endif
