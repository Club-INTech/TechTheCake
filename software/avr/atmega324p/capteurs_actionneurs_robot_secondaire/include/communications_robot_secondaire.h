#ifndef COMMUNICATIONS_ROBOT_SECONDAIRE_H
#define COMMUNICATIONS_ROBOT_SECONDAIRE_H

#include <libintech/serial/serial_0.hpp>

#include "actionneurs_robot_secondaire.h"
#include "capteurs_robot_secondaire.h"

class Communications
{
	public:
		Communications();
        void execute(char ordre[]);

    public:
		typedef Serial<0> serie_robot;
        Actionneurs actionneurs;
        Capteurs capteurs;

};


#endif
