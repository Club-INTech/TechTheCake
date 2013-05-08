#include "actionneurs_robot_secondaire.h"

Actionneurs::Actionneurs():
    verre_gauche(1, 1, 1023),
    verre_droit(2, 1, 1023),
    casse_pile(0, 1, 1023)
{
    serie_ax12::init();
    serie_ax12::change_baudrate(9600);

}

