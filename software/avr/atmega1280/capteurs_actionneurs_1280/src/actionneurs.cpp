#include "actionneurs.h"

Actionneurs::Actionneurs():
    cadeaux(4, AX_ANGLECW_CADEAUX, AX_ANGLECCW_CADEAUX),
    bougies_haut(1, AX_ANGLECW_BOUGIES, AX_ANGLECCW_BOUGIES),
    bougies_bas(3, AX_ANGLECW_BOUGIES, AX_ANGLECCW_BOUGIES)
{
    serie_ax12::init();
    serie_ax12::change_baudrate(9600);

}

