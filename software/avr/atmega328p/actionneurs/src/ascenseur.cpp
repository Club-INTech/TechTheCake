#include <libintech/moteur.hpp>
#include <libintech/serial/serial_0.hpp>


#include "ascenseur.h"
#include "actionneurs.h"


template<class Moteur,class Codeuse>
Ascenseur<Moteur, Codeuse>::Ascenseur():
	_asservissement(0.01,0.00,0.001),
	_compteur_blocage(0),
	_est_asservi(true)
{
	_asservissement.valeur_bridage(175);
}

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::asservir()
{
	codeuse(libcodeuse.compteur());
	int32_t pwm = _asservissement.pwm(_codeuse, 10);
	int32_t derivee_erreur = _asservissement.erreur();
	if (_est_asservi)
	{
		_moteur.envoyerPwm(pwm);
	}
	else
	{
		_moteur.envoyerPwm(0);
	}
	
	// Si blocage moteur
	
	bool bouge_pas = !((derivee_erreur <= 30) && (derivee_erreur >= -30));
	bool moteur_force = (pwm >= 75) || (pwm <= -75);
	if (bouge_pas && moteur_force)
	{
		++_compteur_blocage;
		if (_compteur_blocage >= COMPTEUR_BLOCAGE_MAX)
		{
			// Recalage si blocage en bas
			if (_asservissement.consigne() == ASCENSEUR_BAS) // Si l'ascenseur bloc en bas, alors la codeuse est mise à 0 (fait dans le main)
			{
				libcodeuse.compteur(0);
				_codeuse = 0;
			}
			_compteur_blocage = 0;
			_asservissement.consigne(libcodeuse.compteur());
		}
	}
	else
	{
		_compteur_blocage = 0;
	}
}

/**
 * Envoi de la consigne au moteur
 * en fonction du type enum AscenseurPosition
 * (limité)
 */

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::consigne(AscenseurPosition consigne)
{
	_asservissement.consigne(consigne);
	_compteur_blocage = 0;
}

/**
 * Envoi de la consigne au moteur
 * pour d'autres valeurs
 * (général)
 */

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::consigne(int32_t consigne)
{
	_asservissement.consigne(consigne);
	_compteur_blocage = 0;
}

/**
 * Récupère la valeur de la codeuse associé au moteur
 */

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::codeuse(int32_t c)
{
	_codeuse = c;
}

/**
 * Accesseur codeuse
 */

template<class Moteur,class Codeuse>
int32_t Ascenseur<Moteur, Codeuse>::codeuse()
{
	return _codeuse;
}

/**
 * Désasservir 
 */

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::desasservir()
{
	_est_asservi = false;
}

/**
 * Réasservir
 */

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::reasservir()
{
	_est_asservi = true;
}

template<class Moteur,class Codeuse>
void Ascenseur<Moteur, Codeuse>::modifierVitesseKpKdKi(int8_t PWM, float kp, float kd, float ki)
{
	_asservissement.valeur_bridage(150);
	_asservissement.kp(kp);
	_asservissement.kd(kd);
	_asservissement.ki(ki);
}

template class Ascenseur<Actionneurs::moteur_avant_t, Actionneurs::codeuse_ascenseur_avant>;
//template class Ascenseur<Actionneurs::moteur_arriere_t, Actionneurs::codeuse_ascenseur_arriere>;
