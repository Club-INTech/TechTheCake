// LIBRAIRIES STANDARD
#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// LIBRAIRIE INTECH
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>

// LIBRAIRIES LOCALES
#include <libintech/ax12.hpp>

/********************************
 *           CONSTANTES         *
 ********************************/

#define BAUD_RATE_SERIE         9600
#define BAUD_RATE_AX12          2000000/(BAUD_RATE_SERIE+1)

// Angles MIN et MAX en tics (compris entre 0 et 1024, cf. datasheet)
#define AX_ANGLECW              198
#define AX_ANGLECCW             800

// Vitesse de rotation des AX12 (je crois entre 0 et 1024, pas sûr)
#define AX_SPEED                1000

/******************************** 
 *   MODES DE CONFIGURATION     *   
 ********************************/

// Mode pour reflasher l'id des AX12 connectés. Attention à c'qu'on fait.
// Si ce mode est positif, il reflashera l'id des AX12 à la valeur du mode.
// Pour ne pas reflasher l'id des AX12 connectés, mettre une valeur négative.
    #define FLASH_ID_MODE           -1

// Mode pour reflasher le baud rate d'écoute des AX12. Warning. Achtung.
// Mettre à 0 pour ne pas le reflasher, à 1 sinon. Si ce mode est à 1,
// la carte reflashera le baud rate d'écoute de l'AX12 à la valeur
// BAUD_RATE_AX12 (définie un peu plus haut)
    #define FLASH_BAUD_RATE_MODE    0

// Mode pour tester les AX12 sans utiliser la liaison PC.
// A mettre à 1 pour l'utiliser, à 0 sinon. Si le mode est mis à 1, l'AX12
// ira à un angle de 90°
    #define TEST_NOSERIE_MODE       0

// Mode si l'AX12 ne répond pas alors qu'il le devrait. Vérifier la masse.
// Si ce mode est utilisé, les diodes de l'AX12 clignotent 5 sec après un
// petit bout de temps (de l'ordre de la minute) et sont alors reset.
// Il faudra reflasher leur baud-rate après (en utilisant le mode ci dessus)
// NOTE : Pour reflasher leur baud-rate, il faudra remettre le baud rate de la
// série de la carte à 1.000.000. (c'est le baud-rate d'écoute 
// Cette solution est dégueux : elle teste tous les baud rate possibles et
// envoie un signal de réset. Si l'AX12 ne répond pas, c'est un problème
// matériel. Vérifier la masse, puis faire revérifier la masse par un 2A
    #define REANIMATION_MODE        0



typedef Serial<0> serial_t_;




int main(int argc, char const *argv[])
{

    serial_t_::init();
    serial_t_::change_baudrate(BAUD_RATE_SERIE);
    
    // REANIMATION_MODE :
    uint8_t debug_baudrate = 0x00;

 

    AX<serial_t_, BAUD_RATE_AX12> AX4(0xFE, 0, 0x3ff, 0x1ff);
    AX<serial_t_, BAUD_RATE_AX12> AX1337(0xFE, 0, 0x3ff, 0x1ff);
    AX<serial_t_, BAUD_RATE_AX12> Tableau_AX[] = {AX4, AX1337};

    while(1){
            
            char buffer[17];
            serial_t_::read(buffer);

            // Ping
            if(strcmp(buffer, "?") == 0)
            {
                serial_t_::print(3);
            }
            
            
            // Easter Egg
            else if(strcmp(buffer, "sopa") == 0)
            {
                serial_t_::print("SOPAL'INT\n\r-------\n\n\rSopal'INT VA VOUS METTRE\n\r\
                                    LA RACE !!!!\n\r***********");
                serial_t_::print("STOP SOPA ! START SOPAL'INT");
            }
            
            // AIDE
            else if(strcmp(buffer, "!") == 0)
            {
                serial_t_::print("Salut vieux ! Comment vas-tu aujourd'hui ?");
            }
            
            /// *********************************************** ///
            ///                 ACTIONNEURS                     ///
            /// *********************************************** ///
            
            // Initialisation des AX12
            else if(strcmp(buffer, "i") == 0)
            {
                AX1337.init(AX_ANGLECW, AX_ANGLECCW, AX_SPEED);
            }
              
            // GoTo angle
            else if(strcmp(buffer, "goto") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_t_::read(id);
                serial_t_::read(angle);
                Tableau_AX[id].GoTo(AX_ANGLECW + (uint16_t)(600.*angle/180.)); // Formule à revoir
            }
            
            // Goto brut
            else if(strcmp(buffer, "gotobrut") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_t_::read(id);
                serial_t_::read(angle);
                
                Tableau_AX[id].GoTo(angle);
            }
            
            // Changement de vitesse
            else if(strcmp(buffer, "ch_vit") == 0)
            {
                uint8_t  id;
                uint16_t speed;
                
                serial_t_::read(id);
                serial_t_::read(speed);
                
                Tableau_AX[id].changeSpeed(speed);
            }
            
            // Changement de l'angleCW (min)
            else if(strcmp(buffer, "m") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_t_::read(id);
                serial_t_::read(angle);
                
                Tableau_AX[id].changeAngleMIN(angle);
            }
            
            // Changement de l'angle CCW (max)
            else if(strcmp(buffer, "m") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_t_::read(id);
                serial_t_::read(angle);
                
                Tableau_AX[id].changeAngleMAX(angle);
            }             
            
            // Reflashage des Ids de tous les servos branchés
            else if(strcmp(buffer, "f") == 0)
            {
                uint8_t ancien_id;
                uint8_t nouvel_id;
                
                serial_t_::read(ancien_id);
                serial_t_::read(nouvel_id);
                
                Tableau_AX[ancien_id].initID(nouvel_id);
            }
            
            // Désasservissement d'un AX12
            else if(strcmp(buffer, "UNASSERV") == 0 || strcmp(buffer, "u") == 0 )
            {
                uint8_t id;

                serial_t_::read(id);
                Tableau_AX[id].unasserv();                
            }            
            
            else if (strcmp(buffer, "t") == 0)
            {
                uint8_t id;
                uint8_t temperature;

                serial_t_::read(id);
                serial_t_::read(temperature);

                Tableau_AX[id].changeT(temperature);
                serial_t_::print("ok");
            }

            else if (strcmp(buffer, "vm") == 0)
            {
                uint8_t id;
                uint8_t volt;

                serial_t_::read(id);
                serial_t_::read(volt);

                Tableau_AX[id].changeVMin(volt);
                serial_t_::print("ok");
            }

            else if (strcmp(buffer, "vM") == 0)
            {
                uint8_t id;
                uint8_t volt;

                serial_t_::read(id);
                serial_t_::read(volt);

                Tableau_AX[id].changeVMax(volt);
                serial_t_::print("ok");
            }

            // LEDs d'alarme.
            else if (strcmp(buffer, "led") == 0)
            {
                uint8_t id;
                uint8_t type;

                serial_t_::read(id);
                serial_t_::read(type);
                
                Tableau_AX[id].led(type);
            }


            
            // Message générique. Utilisable pour modifier n'importe quoi.
            else if (strcmp(buffer, "message") == 0)
            {
                uint8_t id;
                uint8_t adresse;
                uint8_t n;
                uint16_t val;
                
                serial_t_::read(id);
                serial_t_::read(adresse);
                serial_t_::read(n);
                serial_t_::read(val);
                
                Tableau_AX[id].message(adresse, n, val);   
            }
            
            else if (strcmp(buffer, "reanim") == 0)
            {
                serial_t_::print("id? (0xFE pour ne pas reflasher l'ID)");
                uint8_t id;
                
                serial_t_::read(id);
                Tableau_AX[id].reanimationMode();
            } 
    }
    return 0;
}








