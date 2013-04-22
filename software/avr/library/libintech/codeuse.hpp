#ifndef CODEUSE_HPP 
#define CODEUSE_HPP

#include "register.hpp"

template<class PinA, class PinB, bool DeuxCanaux>
class Codeuse
{

private:
	int32_t _compteur;
	uint8_t mb;  //Mise en mémoire de l'ancienne valeur de cb

public:
	Codeuse():
		_compteur(0)
	{
		//Mise en lecture des Pins des codeuses
		PinA::set_input();
		PinB::set_input();

		// Initialisation interruptions codeurs
		PinB::set_interrupt();
        if (DeuxCanaux) PinA::set_interrupt();

		mb = PinB::read();
	}
	inline void interruption()
	{
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
