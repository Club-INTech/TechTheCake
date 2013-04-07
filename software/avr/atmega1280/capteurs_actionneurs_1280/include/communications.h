#ifndef COMMUNICATIONS_H
#define COMMUNICATIONS_H

#include <libintech/serial/serial_0.hpp>

#include "actionneurs.h"
#include "capteurs.h"


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
