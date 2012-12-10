#include <avr/io.h>
#include <libintech/pwm.hpp>
#include <stdint.h>
#include <libintech/utils.h>
#include <libintech/moteur.hpp>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/timer.hpp>

#define vitesse_deplacement_moteur 150 //valeur à changer si trop lent ou trop rapide

int pwm1;
typedef PWM<0,ModeFastPwm,1,'A'> pwm;
Moteur< pwm,AVR_PORTB <PORTB5> > moteur;
int main ()
{
	Serial<0>::init();
	Serial<0>::change_baudrate(9600);
	moteur.maxPWM(255);
	typedef Timer<1,8> Timer1;
	Timer1::init();
	sei();
	sbi(DDRB, DDB4); //brake
	cbi(DDRB, DDB3); //entrée capteur fin de course haut
	cbi(DDRB, DDB2); //entrée capteur fin de course bas
	char ordre[8];
	while (1)
	{
		if ((strcmp(ordre, "haut") == 0) && (rbi(PORTB, PORTB3) == 0))
		{
			cbi(PORTB, PORTB4);
			pwm1 = vitesse_deplacement_moteur;
			moteur.envoyerPwm(pwm1);
		}
		else if ((strcmp(ordre, "bas") == 0) && (rbi(PORTB, PORTB2) == 0))
		{
			cbi(PORTB, PORTB4);
			pwm1 = - vitesse_deplacement_moteur;
			moteur.envoyerPwm(pwm1);
		}
	}
}


ISR(TIMER1_OVF_vect)
{
	if ((rbi(PORTB, PORTB3) == 1 && pwm1 >= 1))
	{
		sbi(PORTB, PORTB4);
		moteur.envoyerPwm(255);
	}
	else if ((rbi(PORTB, PORTB2) == 1 && pwm1 <= - 1))
	{
		sbi(PORTB, PORTB4);
		moteur.envoyerPwm(255);
	}
	else 
	{
		cbi(PORTB, PORTB4);
	}

}
