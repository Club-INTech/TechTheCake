#include <avr/io.h>
#include <libintech/pwm.hpp>
#include <stdint.h>
#include <libintech/utils.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/moteur.hpp>
#include <libintech/timer.hpp>

#include "compteur.h"

#define valeur_critique 15 // ~ 1 sec
#define AQUITTER Serial<0>::print("_")
/**

*Pin 13 -> dir

*Pin 6 -> PWM

*Pin 2 -> 1er signal codeuse

*Pin 3 -> 2eme signal codeuse

*Pour changer la vitesse max, modifier la valeur de moteur.maxPWM().

*Si le moteur diverge totalement, essayez d'intervertir 

**/
	int32_t pos;
	int32_t erreur;
	int32_t erreur_ancienne = 0;
	int32_t derivee = 0;
	int32_t pwm1;
	int32_t integrale;
	double kp=0.1;
	double ki=0.0001;
	double kd=0.01;
	bool moteur_force;
	bool bouge_pas;
	uint8_t vitesse_max = 175;
	uint8_t i = 0;

int main()
{
	Serial<0>::init();
	Serial<0>::change_baudrate(9600);
	typedef Timer<1,8> Timer1;
	Timer1::init();
	sei();
	compteur_init();
	char ordre[8];
	while (1)
	{
		Serial<0>::read(ordre);
		AQUITTER;
		if (strcmp(ordre, "pos") == 0) // Position voulue
		{
			Serial<0>::print("Position voulue?");
			Serial<0>::read(pos);
			integrale = 0;
			i = 0;
		}
		if (strcmp(ordre, "?") == 0) // Position voulue
		{
			Serial<0>::print("2");
		}
		if (strcmp(ordre, "haut") == 0) // Hauteur d'un verre
		{
			pos = 46000;
			integrale = 0;
			i = 0;
		}
		if (strcmp(ordre, "bas") == 0) // en bas
		{
			pos = 0;
			integrale = 0;
			i = 0;
		}
		if (strcmp(ordre, "max") == 0) // Vitesse Max vouleur
		{
			Serial<0>::print("Vitesse Max voulue?");
			Serial<0>::read(vitesse_max);
		}
		if (strcmp(ordre, "stop") == 0) // Asservir sur la position courante
		{
			pos = roue1;
		}
		if (strcmp(ordre, "kp") == 0) // kp voulue
		{
			Serial<0>::print("kp voulue?");
			Serial<0>::read(kp);
		}
		if (strcmp(ordre, "ki") == 0) // ki voulue
		{
			Serial<0>::print("ki voulue?");
			Serial<0>::read(ki);
		}
		if (strcmp(ordre, "kd") == 0) // kd voulue
		{
			Serial<0>::print("kd voulue?");
			Serial<0>::read(kd);
		}
	}
}
ISR(TIMER1_OVF_vect)
{
	/*
	Asservissement:
	*/
	typedef PWM<0,ModeFastPwm,1,'A'> pwm;
	Moteur< pwm,AVR_PORTB <PORTB5> > moteur;
	moteur.maxPWM(vitesse_max);
	erreur = pos - roue1;
	integrale += erreur;
	pwm1 = kp * erreur + ki * integrale + kd * (erreur - erreur_ancienne);
	moteur.envoyerPwm(pwm1);
	derivee = erreur - erreur_ancienne;
	erreur_ancienne = erreur;

	/*
	Si blocage moteur:
	*/
	bouge_pas = derivee <= 30 || derivee >= -30;
	moteur_force = (pwm1 > 30) || (pwm1 < -30);
	if (bouge_pas && moteur_force)
	{
		++i;
		if (i > valeur_critique )
		{
			pos = roue1;
			integrale = 0;
			/*if ((roue1 >= 1000) && (pos == 0))
			{
				roue1 = 0;
				pos = 0;
			}*/
		}
	}
	else
	{
		i = 0;
	}
}
