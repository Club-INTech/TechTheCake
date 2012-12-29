#ifndef ASCENCEUR_H
#define ASCENCEUR_H

#include <libintech/moteur.hpp>

template<class Moteur>
class Ascenceur
{
	public:
		Ascenceur();
		void asservir();
	private:
		Moteur moteur;
};

#endif
