#ifndef CODEUSE_HPP 
#define CODEUSE_HPP

#include "register.hpp"

template<class PinA, class PinB>
class Codeuse
{
private:
	int32_t _compteur;

public:
	Codeuse():
		_compteur(0)
	{
		//Mise en lecture des Pins des codeuses
		PinA::set_input();
		PinB::set_input();

		// Initialisation interruptions codeurs
		PinA::set_interrupt();
		PinB::set_interrupt();
	}

	inline void interruption()
	{
		uint8_t mb = PinB::read(); //Mise en mémoire de l'ancienne valeur de cb

		if(PinA::read() == mb) ++_compteur; // Test du sens de rotation de la roue. Ecrire la table de vérité pour comprendre.
		else --_compteur;

		mb = PinB::read(); //Mise en mémoire de l'ancienne valeur de cb
	}

	inline int32_t compteur()
	{
		return _compteur;
	}

	inline void compteur(int32_t c)
	{
		_compteur = c;
	}

};

#endif