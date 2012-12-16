#include <libintech/moteur.hpp>
#include "ascenceur.h"
#include "actionneurs.h"

template<class Moteur>
Ascenceur<Moteur>::Ascenceur(){
		moteur.maxPWM(255);
}

template class Ascenceur<Actionneurs::moteur_avant_t>;
