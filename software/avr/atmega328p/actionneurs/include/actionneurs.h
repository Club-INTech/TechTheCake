#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/singleton.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/pwm.hpp>
#include <libintech/moteur.hpp>
#include <libintech/timer.hpp>

#include "ascenceur.h"
#include "compteur_1.h"

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
		typedef Timer<1,8> timer_asserv;
		/**
		 * Ascenceur avant, dépend d'un moteur
		 * 
		 */
		Ascenceur< moteur_avant_t > ascenceur_avant;
		Ascenceur< moteur_arriere_t > ascenceur_arriere;

	public:
		Actionneurs();
		/**
		 * Execute les ordres reçus sur la série
		 * 
		 */
		void execute(char*);
};

#endif
