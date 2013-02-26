#include "actionneurs.h"

Actionneurs::Actionneurs():
    cadeaux(4, AX_ANGLECW, AX_ANGLECCW)
{
    serie_ax12::init();
    serie_ax12::change_baudrate(9600);

}

