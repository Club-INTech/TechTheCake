#include <libintech/moteur.hpp>
#include "ascenceur.h"
#include "actionneurs.h"

#define valeur_critique 15 // ~ 1 sec (à vérifier)

template<class Moteur>
Ascenceur<Moteur>::Ascenceur(){
	moteur.maxPWM(255);
}
void Ascenceur::asservir()
{
	/*
	Je définis mes variables ici, car sinon, il ne compile pas... J'ai essayé de le mettre dans le "public" et dans le "private" d'ascenceur.h et d'actionneurs.h, mais il me jette à chaque fois.
	*/
	int32_t pos;
	int32_t erreur;
	int32_t erreur_ancienne;
	int32_t derivee = 0;
	int32_t pwm;
	int32_t integrale;
	double kp = 0.1;
	double kd = 0.01;
	double ki = 0.0001;
	bool moteur_force;
	bool bouge_pas;
	uint8_t i = 0;
	/*
	Asservissement:
	*/
	erreur = pos - codeuse;
	integrale += erreur;
	pwm = kp * erreur + ki * integrale + kd * (erreur - erreur_ancienne);
	Moteur.envoyerPwm(pwm);
	derivee = erreur - erreur_ancienne;
	erreur_ancienne = erreur;
	/*
	Si blocage moteur:
	*/
	bouge_pas = (derivee <=30) || (derivee >= -30);
	moteur_force = (pwm >= 30) || (pwm <= -30);
	if (bouge_pas && moteur_force)
	{
		++i;
		if (i > valeur_critique)
		{
			pos = codeuse;
			integrale = 0;
		}
	}
	else
	{
		i = 0;
	}
}

template class Ascenceur<Actionneurs::moteur_avant_t>; // Je ne comprend pas cette ligne
