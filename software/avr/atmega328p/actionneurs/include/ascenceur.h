#ifndef ASCENCEUR_H
#define ASCENCEUR_H

#include <libintech/moteur.hpp>

template<class Moteur>
class Ascenceur
{
public:
	Ascenceur();
private:
	Moteur moteur;

};

#endif
