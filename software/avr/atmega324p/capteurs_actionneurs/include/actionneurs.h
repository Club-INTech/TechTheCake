#ifndef ACTIONNEURS_H
#define ACTIONNEURS_H

#include <libintech/ax12.hpp>
#include <libintech/serial/serial_1.hpp>

#define AX_ANGLECW_CADEAUX              1
#define AX_ANGLECCW_CADEAUX             1023

#define AX_ANGLECW_BOUGIES              205 //angle min >0
#define AX_ANGLECCW_BOUGIES             818 //angle max <1024

/**
 * Gestion des actionneurs
 * 
 */

class Actionneurs
{
	public:
		typedef Serial<1> serie_ax12;
        typedef AX<serie_ax12> Ax12;
        AX<serie_ax12> cadeaux;
        AX<serie_ax12> bougies_haut;
        AX<serie_ax12> bougies_bas;

	public:
		Actionneurs();

};

#endif
