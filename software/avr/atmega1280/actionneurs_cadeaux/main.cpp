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
#define AX_ANGLECW              205
#define AX_ANGLECCW             818

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

typedef AX<serial_AX_, BAUD_RATE_AX12> AX12;

int main(int argc, char const *argv[])
{
    serial_AX_::init();
    serial_AX_::change_baudrate(BAUD_RATE_SERIE);

    serial_PC_::init();
    serial_PC_::change_baudrate(BAUD_RATE_SERIE);
    
    // REANIMATION_MODE :
    //uint8_t debug_baudrate = 0x00;

 
    AX12 AX4(4, AX_ANGLECW, AX_ANGLECCW);

    AX12 Tableau_AX[] = {AX4};

    while(1){
            
            char buffer[17];
            serial_PC_::read(buffer);

            if(strcmp(buffer, "g") == 0)
            {
                uint16_t angle;
                
                serial_PC_::read(angle);
                Tableau_AX[0].goTo(angle); //Angle d'entrée commandé
                serial_PC_::print("Déplacement effectué\n");
            }
            
            // Changement de vitesse
            else if(strcmp(buffer, "ch_vit") == 0)
            {	
                uint16_t speed;
                
                serial_PC_::read(speed);
                
                Tableau_AX[0].changeSpeed(speed);
                serial_PC_::print("Vitesse modifiée\n");
            }

            else
            {
                serial_PC_::print("Donne moi une commande que je connais !\n");
            } 
    }
    return 0;
}








