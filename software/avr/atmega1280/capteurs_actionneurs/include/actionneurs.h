#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/ax12.hpp>
#include <libintech/serial/serial_1.hpp>

#define AX_ANGLECW              512
#define AX_ANGLECCW             820

/**
 * Gestion des actionneurs
 * 
 */

class Actionneurs
{
	public:
		typedef Serial<1> serie_ax12;

        AX<serie_ax12> cadeaux;
        AX<serie_ax12> bougies_haut;
        AX<serie_ax12> bougies_bas;

	public:
		Actionneurs();

};

#endif
