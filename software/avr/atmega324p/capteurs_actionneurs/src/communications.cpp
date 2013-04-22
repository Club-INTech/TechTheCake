#include "communications.h"
#include "capteurs.h"
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

        // CAPTEURS
        if (strcmp(ordre, "nbI")==0)   //pour l'initialisation en python du nombre de capteurs
        {
            serie_robot::print(NB_INFRAROUGE_AVANT);
        }
        else if (strcmp(ordre, "nbi")==0)
        {
            serie_robot::print(NB_INFRAROUGE_ARRIERE);
        }
        else if (strcmp(ordre, "nbS")==0)
        {
            serie_robot::print(NB_SRF_AVANT);
        }
        else if (strcmp(ordre, "nbs")==0)
        {
            serie_robot::print(NB_SRF_ARRIERE);
        }

        // infrarouge
        else if (strcmp(ordre, "ir_av")==0)
        {
            serie_robot::print(capteurs.inf2.value());
        }
        else if (strcmp(ordre, "ir_arr")==0)
        {
            serie_robot::print(capteurs.inf1.value());
        }

        // Ultrasons SRF05
        else if (strcmp(ordre, "us_av")==0)
        {
            serie_robot::print(capteurs.us1.value());
        }
        else if (strcmp(ordre, "us_arr")==0)
        {
            serie_robot::print(capteurs.us2.value());
        }


        // Distributeur
        else if (strcmp(ordre, "dist")==0)
        {
            uint16_t delai;
            serie_robot::read(delai);
            sbi(PORTD, PORTD4);
            for(uint16_t i=0; i<delai; i++)
                _delay_ms(1);
            cbi(PORTD, PORTD4);
        }
        else if (strcmp(ordre, "dist_on")==0)
        {
            sbi(PORTD, PORTD4);
        }
        else if (strcmp(ordre, "dist_off")==0)
        {
            cbi(PORTD, PORTD4);
        }

        //serial de la carte (ping)
        else if (strcmp(ordre, "?")==0)
        {
            serie_robot::print(3);
        }

        // ACTIONNEURS CADEAUX        
        else if(strcmp(ordre, "cadeau") == 0)
        {
            uint16_t angle;
            
            serie_robot::read(angle);
            actionneurs.cadeaux.goTo(angle); //Angle d'entrée commandé
        }
/*        
        // Changement de vitesse
        else if(strcmp(ordre, "ch_vit") == 0)
        {	
            uint16_t speed;

            serie_robot::read(speed);
            actionneurs.cadeaux.changeSpeed(speed);
        }
*/
	// ACTIONNEURS ASCENSEURS
        else if(strcmp(ordre, "asc_av") == 0)
        {
          uint16_t angle;
          serie_robot::read(angle);
          actionneurs.asc_avant.goTo(angle);
        }
        else if(strcmp(ordre, "asc_arr") == 0)
        {
          uint16_t angle;
          serie_robot::read(angle);
          actionneurs.asc_arriere.goTo(angle);
        }

        // ACTIONNEURS BOUGIES
        else if(strcmp(ordre, "bas") == 0)
        {
          uint16_t angle;
          serie_robot::read(angle);
          actionneurs.bougies_bas.goTo(angle); //Angle d'entrée commandé
        }
        
        else if(strcmp(ordre, "haut") == 0)
        {
          uint16_t angle;

          serie_robot::read(angle);
          actionneurs.bougies_haut.goTo(angle); //Angle d'entrée commandé
        }

        // JUMPER DE DÉBUT DE MATCH
        else if (strcmp(ordre, "j") == 0)
        {
            serie_robot::print(rbi(PINC,PINC2));
        }

	// CAPTEURS ASCENSEURS
        else if (strcmp(ordre, "cap_asc_av") == 0)
        {
            serie_robot::print(capteurs.ascenseur_avant());
        }

        else if (strcmp(ordre, "cap_asc_arr") == 0)
        {
            serie_robot::print(capteurs.ascenseur_arriere());
        }
}


