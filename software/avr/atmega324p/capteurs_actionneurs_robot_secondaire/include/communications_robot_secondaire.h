#ifndef COMMUNICATIONS_ROBOT_SECONDAIRE_H
#define COMMUNICATIONS_ROBOT_SECONDAIRE_H

#include <libintech/serial/serial_0.hpp>

#include "capteurs_robot_secondaire.h"

class Communications
{
	public:
		Communications();
        void execute(char ordre[]);

    public:
		typedef Serial<0> serie_robot;
        Capteurs capteurs;

};


#endif
