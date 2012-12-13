#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <stdint.h>
#include <avr/io.h>

//~ #include <libintech/singleton.hpp>
//~ #include <libintech/serial/serial_0.hpp>
//~ #include <libintech/serial/serial_0_interrupt.hpp>

//~ typedef Serial<0> serie;

class Actionneurs
{
	public:

		// Déclaration de l'ascenceur_avant
		//~ typedef PWM<0,ModeFastPwm,1,'A'> pwm;
		//~ Moteur<pwm,AVR_PORTB <PORTB5>> moteur;
		//~ Ascenceur<moteur> ascenceur_avant;

		Actionneurs();
		//void execute(char*);

};

#endif
