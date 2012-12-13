#ifndef ASCENCEUR_H
#define ASCENCEUR_H

#include <libintech/moteur.hpp>

template<class Moteur>
class Ascenceur
{
public:
	Ascenceur()
	{
		moteur.maxPWM(255);
	}
	
private:
	Moteur moteur;

};

#endif
