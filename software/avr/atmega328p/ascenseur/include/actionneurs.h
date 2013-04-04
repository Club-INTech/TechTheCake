#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/singleton.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/pwm.hpp>
#include <libintech/moteur.hpp>
#include <libintech/timer.hpp>

#include "ascenseur.h"
#include "twi_master.h"

/**
 * Gestion des actionneurs
 * 
 */
class Actionneurs : public Singleton<Actionneurs>
{
	public:
		typedef Serial<0> serie;
		typedef Moteur< PWM<0,ModeFastPwm,1,'B'>, AVR_PORTD <PORTD4> > moteur_avant_t;
		typedef Moteur< PWM<0,ModeFastPwm,1,'A'>, AVR_PORTB <PORTB0> > moteur_arriere_t;
		typedef Timer<1,64> timer_asserv;
		/**
		 * Ascenceur avant, dépend d'un moteur
		 * 
		 */
		Ascenseur< moteur_avant_t > ascenseur_avant;
		Ascenseur< moteur_arriere_t > ascenseur_arriere;

	public:
		Actionneurs();
		/**
		 * Execute les ordres reçus sur la série
		 * 
		 */
		void communiquer(char*);
};

#endif
