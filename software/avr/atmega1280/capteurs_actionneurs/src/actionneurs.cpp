#include "actionneurs.h"

Actionneurs::Actionneurs():
    cadeaux(4, AX_ANGLECW, AX_ANGLECCW),
    bougies_haut(1, AX_ANGLECW, AX_ANGLECCW),
    bougies_bas(3, AX_ANGLECW, AX_ANGLECCW)
{
    serie_ax12::init();
    serie_ax12::change_baudrate(9600);

}

