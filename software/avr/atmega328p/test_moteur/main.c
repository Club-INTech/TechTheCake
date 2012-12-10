#include <avr/io.h>
#include <libintech/pwm.hpp>
#include <stdint.h>
#include <libintech/utils.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/moteur.hpp>
#include <libintech/timer.hpp>

int main()
{
	Serial<0>::init();
	Serial<0>::change_baudrate(9600);
	char ordre[8];
	typedef PWM<0,ModeFastPwm,1,'A'> pwmd;
	Moteur< pwmd,AVR_PORTB <PORTB0> > MD;
	MD.maxPWM(255);
	typedef PWM<0,ModeFastPwm,1,'B'> pwmg;
	Moteur< pwmg,AVR_PORTD <PORTD4> > MG;
	MG.maxPWM(255);
	int pwm = 0;
	while (1)
	{
		Serial<0>::read(ordre);
		if (strcmp(ordre, "d") == 0)
		{
			Serial<0>::print("pwm moteur droit?");
			Serial<0>::read(pwm);
			MD.envoyerPwm(pwm);
		}
		if (strcmp(ordre, "g") == 0)
		{
			Serial<0>::print("pwm moteur gauche?");
			Serial<0>::read(pwm);
			MG.envoyerPwm(pwm);
		}
	}
	return 1;
}
