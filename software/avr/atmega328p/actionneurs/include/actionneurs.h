#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/singleton.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/pwm.hpp>
#include <libintech/moteur.hpp>
#include <libintech/timer.hpp>
#include <libintech/codeuse.hpp>

#include "ascenseur.h"

/**
 * Gestion des actionneurs
 * 
 */
class Actionneurs : public Singleton<Actionneurs>
{
	public:
		typedef Serial<0> serie;
		typedef Moteur< PWM<0,ModeFastPwm,1,'A'>, AVR_PORTB <PORTB5> > moteur_avant_t;
		typedef Moteur< PWM<0,ModeFastPwm,1,'B'>, AVR_PORTB <PORTB4> > moteur_arriere_t;
		typedef Timer<1,64> timer_asserv;
		typedef Codeuse< AVR_PORTD <PORTD2> , AVR_PORTD <PORTD3> > codeuse_ascenseur_avant;
	//	typedef Codeuse< PCINT, > codeuse_ascenseur_arriere;
		/**
		 * Ascenceur avant, dépend d'un moteur
		 * 
		 */
		Ascenseur< moteur_avant_t, codeuse_ascenseur_avant > ascenseur_avant;
	//	Ascenseur< moteur_arriere_t, codeuse_ascenseur_arriere > ascenseur_arriere;

	public:
		Actionneurs();
		/**
		 * Execute les ordres reçus sur la série
		 * 
		 */
		void execute(char*);
};

#endif
