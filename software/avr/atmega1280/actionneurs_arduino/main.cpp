// LIBRAIRIES STANDARD
#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// LIBRAIRIE INTECH
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/serial/serial_1_interrupt.hpp>
#include <libintech/serial/serial_1.hpp>

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

// Vitesse de rotation des AX12 (je crois entre 0 et 1023, pas sûr)
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

typedef Serial<0> serial_PC_;
typedef Serial<1> serial_AX_;

typedef AX<serial_AX_> AX12;

int main(int argc, char const *argv[])
{
    serial_AX_::init();
    serial_AX_::change_baudrate(BAUD_RATE_SERIE);

    serial_PC_::init();
    serial_PC_::change_baudrate(BAUD_RATE_SERIE);
    
    // REANIMATION_MODE :
    //uint8_t debug_baudrate = 0x00;

 
    AX12 AX4(4, 0, 0x3ff);
    AX12 AX0(0, 0, 0x3ff);
    AX12 AX1(1, 0, 0x3ff);
    AX12 AX2(2, 0, 0x3ff);
    AX12 AX3(3, 0, 0x3ff);

    AX12 Tableau_AX[] = {AX0, AX1, AX2, AX3, AX4};

    while(1){
            
            char buffer[17];
            serial_PC_::read(buffer);

            if (strcmp(buffer, "?") == 0)
            {
                serial_PC_::print(0);
            }
            
            /// *********************************************** ///
            ///                 ACTIONNEURS                     ///
            /// *********************************************** ///
            
            // Initialisation des AX12
            /*else if(strcmp(buffer, "i") == 0)
            {
                AX1337.init(AX_ANGLECW, AX_ANGLECCW, AX_SPEED);
                serial_PC_::print("AX12 initialisés\n");
            }*/
              
            // GoTo angle
            else if(strcmp(buffer, "g") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_PC_::read(id);
                serial_PC_::read(angle);
                Tableau_AX[id].goTo(angle); //Angle d'entrée commandé
                serial_PC_::print("Déplacement effectué\n");
            }

            else if(strcmp(buffer, "gb") == 0)
            {
                uint16_t angle;
                serial_PC_::read(angle);
                AX12::goToB(angle); //Angle d'entrée commandé
                serial_PC_::print("Déplacement effectué\n");
            }
	            
            // Changement de vitesse
            else if(strcmp(buffer, "ch_vit") == 0)
            {
                uint8_t  id;
                uint16_t speed;
                
                serial_PC_::read(id);
                serial_PC_::read(speed);
                
                Tableau_AX[id].changeSpeed(speed);
                serial_PC_::print("Vitesse modifiée\n");
            }
            
            // Changement de l'angleCW (min)
            else if(strcmp(buffer, "m") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_PC_::read(id);
                serial_PC_::read(angle);
                
                Tableau_AX[id].changeAngleMIN(angle);
                serial_PC_::print("Angle minimal modifié\n");
            }
            
            // Changement de l'angle CCW (max)
            else if(strcmp(buffer, "M") == 0)
            {
                uint8_t id;
                uint16_t angle;
                
                serial_PC_::read(id);
                serial_PC_::read(angle);
                
                Tableau_AX[id].changeAngleMAX(angle);
                serial_PC_::print("Angle maximum modifié\n");                
            }             
            
            // Reflashage de l'ID d'un AX12
            else if(strcmp(buffer, "f") == 0)
            {
                uint8_t ancien_id;
                uint8_t nouvel_id;
                
                serial_PC_::read(ancien_id);
                serial_PC_::read(nouvel_id);
                
                Tableau_AX[ancien_id].initID(nouvel_id);
                serial_PC_::print("ID des AX12 reflashés\n");                
            }
            
            // Désasservissement d'un AX12
            else if(strcmp(buffer, "UNASSERV") == 0 || strcmp(buffer, "u") == 0 )
            {
                uint8_t id;

                serial_PC_::read(id);
                Tableau_AX[id].unasserv();
                serial_PC_::print("AX12 désaservi\n");                
            }            
            
            // Modification de la température maximale
            else if (strcmp(buffer, "t") == 0)
            {
                uint8_t id;
                uint8_t temperature;

                serial_PC_::read(id);
                serial_PC_::read(temperature);

                Tableau_AX[id].changeT(temperature);
                serial_PC_::print("Température maximale modifiée\n");
            }

            // Modification du voltage minimal
            else if (strcmp(buffer, "vm") == 0)
            {
                uint8_t id;
                uint8_t volt;

                serial_PC_::read(id);
                serial_PC_::read(volt);

                Tableau_AX[id].changeVMin(volt);
                serial_PC_::print("Voltage minimal modifié\n");
            }

            // Modification du voltage minimal
            else if (strcmp(buffer, "vM") == 0)
            {
                uint8_t id;
                uint8_t volt;

                serial_PC_::read(id);
                serial_PC_::read(volt);

                Tableau_AX[id].changeVMax(volt);
                serial_PC_::print("Voltage maximal modifié\n");
            }

            // LEDs d'alarme.
            else if (strcmp(buffer, "led") == 0)
            {
                uint8_t id;
                uint8_t type;

                serial_PC_::read(id);
                serial_PC_::read(type);
                
                Tableau_AX[id].led(type);
                serial_PC_::print("La commande que je sais pas ce qu'elle fait mais qu'a été effectuée\n");
            }


            
            // Message générique. Utilisable pour modifier n'importe quoi.
            else if (strcmp(buffer, "message") == 0)
            {
                uint8_t id;
                uint8_t adresse;
                uint8_t n;
                uint16_t val;
                
                serial_PC_::read(id);
                serial_PC_::read(adresse);
                serial_PC_::read(n);
                serial_PC_::read(val);
                
                Tableau_AX[id].message(adresse, n, val);
                serial_PC_::print("Tu veux faire le bogoss en utilisant tes propres commandes ? C'est fait champion !\n");   
            }
            
            else if (strcmp(buffer, "reanim") == 0)
            {
                serial_PC_::print("id? (0xFE pour ne pas reflasher l'ID)\n");
                uint8_t id;
                
                serial_PC_::read(id);
                Tableau_AX[id].reanimationMode(BAUD_RATE_SERIE);
                serial_PC_::print("AX12 reflaché !\n");
            }

            else
            {
                serial_PC_::print("Donne moi une commande que je connais !\n");
            } 
    }
    return 0;
}
