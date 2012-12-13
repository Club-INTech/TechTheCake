#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/singleton.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_0_interrupt.hpp>

class Actionneurs : public Singleton<Actionneurs>
{
	public:
		typedef Serial<0> serie;

		//Déclaration de l'ascenceur_avant
		typedef PWM<0,ModeFastPwm,1,'A'> pwm;
		Moteur<pwm,AVR_PORTB <PORTB5>> moteur;
		Ascenceur<moteur> ascenceur_avant;

	public:
		Actionneurs();
		void execute(char*);

};

#endif
