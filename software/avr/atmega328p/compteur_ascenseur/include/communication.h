#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <libintech/singleton.hpp>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <libintech/codeuse.hpp>

#include "slave.h"

/**
 * Gestion des actionneurs
 * 
 */
class Communication : public Singleton<Communication>
{
	public:
		typedef Codeuse<AVR_PORTD <PORTD2>,AVR_PORTD <PORTD3> > codeuseAvant;
		typedef Codeuse<AVR_PORTD <PORTD4>,AVR_PORTD <PORTD5> > codeuseArriere;
		codeuseAvant codeuseMoteurAvant;
		codeuseArriere codeuseMoteurArriere;

	public:
		Communication();

		void envoyer();
};

#endif
