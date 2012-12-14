#include <libintech/moteur.hpp>
#include "ascenceur.h"

template<class Moteur>
Ascenceur<Moteur>::Ascenceur(){
		moteur.maxPWM(255);
}

template class Ascenceur< Moteur< PWM<0,ModeFastPwm,1,'A'>, AVR_PORTB <PORTB5> > >;
