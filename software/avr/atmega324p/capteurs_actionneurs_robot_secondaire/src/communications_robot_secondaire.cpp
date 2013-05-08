#include "communications_robot_secondaire.h"
#include "libintech/utils.h"
#include <util/delay.h>

Communications::Communications()
{
    sbi(PCMSK3,PCINT29); //active l'interruption sur le port D5
    sbi(PCMSK3,PCINT30); //active l'interruption sur le port D6
    sbi(PCICR,PCIE3);//active PCINT3
    sbi(DDRD,DDD4);//Pin distributeur en sortie
    serie_robot::init();
    serie_robot::change_baudrate(9600);
}

void Communications::execute(char ordre[])
{

        // infrarouge
        if (strcmp(ordre, "ir")==0)
        {
            serie_robot::print(capteurs.ir.value());
        }

        // Ultrasons SRF05
        else if (strcmp(ordre, "us")==0)
        {
            serie_robot::print(capteurs.us.value());
        }
        //serial de la carte (ping)
        else if (strcmp(ordre, "?")==0)
        {
            serie_robot::print(3);
        }
}


