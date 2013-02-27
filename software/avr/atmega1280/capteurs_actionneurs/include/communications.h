#ifndef COMMUNICATIONS_H
#define COMMUNICATIONS_H

#include <libintech/singleton.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/jumper.hpp>

#include "actionneurs.h"
#include "capteurs.h"


class Communications
{
	public:
		Communications();
        void execute(char ordre[]);

    public:
		typedef Serial<0> serie_robot;
        typedef jumper< AVR_PORTC<PORTC1> > jumper_t_;
        Actionneurs actionneurs;
        Capteurs capteurs;       

};


#endif
