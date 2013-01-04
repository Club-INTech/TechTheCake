#include <libintech/moteur.hpp>
#include "ascenceur.h"
#include "actionneurs.h"

template<class Moteur>
Ascenceur<Moteur>::Ascenceur():
	_asservissement(0.1,0.01,0.0001),
	_compteur_blocage(0)
{
	_moteur.maxPWM(255);
}

template<class Moteur>
void Ascenceur<Moteur>::asservir()
{
	int32_t pwm = _asservissement.pwm(_codeuse);
	int32_t derivee_erreur = _asservissement.erreur_d();
	_moteur.envoyerPwm(pwm);
	
	//Si blocage moteur:
	
	bool bouge_pas = (derivee_erreur <=30) || (derivee_erreur >= -30);
	bool moteur_force = (pwm >= 30) || (pwm <= -30);
	if (bouge_pas && moteur_force)
	{
		++_compteur_blocage;
		if (_compteur_blocage >= COMPTEUR_BLOCAGE_MAX)
		{
			// Recalage si blocage en bas
			if (_asservissement.consigne() == ASCENSEUR_BAS)
			{
				_codeuse = ASCENSEUR_BAS;
			}
			_asservissement.consigne(_codeuse);
		}
	}
	else
	{
		_compteur_blocage = 0;
	}
}

template<class Moteur>
void Ascenceur<Moteur>::consigne(AscenseurPosition consigne)
{
	_asservissement.consigne(consigne);
	_compteur_blocage = 0;
}

template class Ascenceur<Actionneurs::moteur_avant_t>;
template class Ascenceur<Actionneurs::moteur_arriere_t>;
