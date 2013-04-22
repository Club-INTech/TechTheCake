#include "actionneurs.h"
#include "ascenseur.h"

template<class Moteur>
Ascenseur<Moteur>::Ascenseur():
	_asservissement(0.01,0,0),
	_compteur_blocage(0),
	_codeuse(0),
	_offset(0)
{
	_asservissement.valeur_bridage(150);
}

template<class Moteur>
void Ascenseur<Moteur>::asservir()
{
	int32_t pwm = _asservissement.pwm(_codeuse);
	int32_t derivee_erreur;
	bool bouge_pas;
	bool moteur_force;
	_moteur.envoyerPwm(pwm);

	// Si blocage moteur
	derivee_erreur = _asservissement.erreur_d();
	bouge_pas = (derivee_erreur <= 10) && (derivee_erreur >= -10);
	moteur_force = (pwm >= 40) || (pwm <= -40);
	if (bouge_pas && moteur_force)
	{
		++_compteur_blocage;
		if (_compteur_blocage >= COMPTEUR_BLOCAGE_MAX)
		{
			if (_asservissement.consigne() == ASCENSEUR_BAS)
			{
				_offset += -_codeuse;
			}
			_compteur_blocage = 0;
			_asservissement.consigne(_codeuse);
		}
	}
	else
	{
		_compteur_blocage = 0;
	}
}

template<class Moteur>
void Ascenseur<Moteur>::modifierVitesseKpKdKi(uint8_t bridage, float kp, float kd, float ki)
{
	_asservissement.valeur_bridage(bridage);
	_asservissement.kp(kp);
	_asservissement.kd(kd);
	_asservissement.ki(ki);
}

template<class Moteur>
void Ascenseur<Moteur>::consigne(int32_t consigne)
{
	_asservissement.consigne(consigne);
	_compteur_blocage = 0;
}

template<class Moteur>
void Ascenseur<Moteur>::consigne(AscenseurPosition consigne)
{
	_asservissement.consigne(consigne);
	_compteur_blocage = 0;
}

template<class Moteur>
void Ascenseur<Moteur>::changerValeurCodeuse(int32_t position)
{
	_codeuse = position + _offset;
}

template<class Moteur>
int32_t Ascenseur<Moteur>::valeurCodeuse()
{
	return _codeuse;
}

template<class Moteur>
int32_t Ascenseur<Moteur>::consigne()
{
	return _asservissement.consigne();
}

template class Ascenseur<Actionneurs::moteur_avant_t>;
template class Ascenseur<Actionneurs::moteur_arriere_t>;
