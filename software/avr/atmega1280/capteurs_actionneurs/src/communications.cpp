#include "communications.h"
#include "capteurs.h"

Communications::Communications()
{
}

void Communications::execute(char ordre[])
{

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
        else if (strcmp(ordre, "i")==0) //minuscule: arrière. Majuscule: avant
        {
            serie_robot::print(capteurs.inf1.value());
        }
        else if (strcmp(ordre, "I")==0)
        {
            serie_robot::print(capteurs.inf2.value());
        }

        // Ultrasons SRF05
        else if (strcmp(ordre, "S")==0)
        {
            serie_robot::print(capteurs.us1.value());
        }
        else if (strcmp(ordre, "s")==0)
        {
            serie_robot::print(capteurs.us2.value());
        }

        //serial de la carte (ping)
        else if (strcmp(ordre, "?")==0)
        {
            serie_robot::print(3);
        }

        // ACTIONNEURS CADEAUX
        
        else if(strcmp(ordre, "g") == 0)
        {
            uint16_t angle;
            
            serie_robot::read(angle);
            actionneurs.cadeaux.goTo(angle); //Angle d'entrée commandé

            // serial_PC_::print("Déplacement effectué\n");
        }
        
        // Changement de vitesse
        else if(strcmp(ordre, "ch_vit") == 0)
        {	
            uint16_t speed;
            
            serie_robot::read(speed);
            
            actionneurs.cadeaux.changeSpeed(speed);

        }

        // ACTIONNEURS BOUGIES

}

