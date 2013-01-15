#ifndef CODEUSE_HPP 
#define CODEUSE_HPP

#include "register.hpp"

template<class PinA, class PinB>
class Codeuse
{
private:
	int32_t _compteur;

public:
	inline static void init()
	{
		//Mise en lecture des Pins des codeuses
		PinA::set_input();
		PinB::set_input();

		// Initialisation interruptions codeurs
		PinA::set_interrupt();
		PinB::set_interrupt();
	}

	void interruption()
	{
		static uint8_t ma = PinA::read(); //Mise en mémoire de l'ancienne valeur de ca
		static uint8_t mb = PinB::read(); //Mise en mémoire de l'ancienne valeur de cb

		if(PinA::read() == mb) ++_compteur; // Test du sens de rotation de la roue. Ecrire la table de vérité pour comprendre.
		else --_compteur;

		ma = PinA::read(); //Mise en mémoire de l'ancienne valeur de ca
		mb = PinB::read(); //Mise en mémoire de l'ancienne valeur de cb
	}

	int32_t compteur()
	{
		return _compteur;
	}

	void compteur(int32_t c)
	{
		_compteur = c;
	}

};

#endif