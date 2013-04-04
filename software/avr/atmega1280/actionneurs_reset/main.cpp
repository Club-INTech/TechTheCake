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

// IDENTIFIANT DE L'AX12 À RÉANIMER 
#define ID_AX 			4



// Le reste des constantes est inutile
#define BAUD_RATE_SERIE         9600
#define BAUD_RATE_AX12          2000000/(BAUD_RATE_SERIE+1)

// Angles MIN et MAX en tics (compris entre 0 et 1024, cf. datasheet)
#define AX_ANGLECW              0
#define AX_ANGLECCW             1024


// Vitesse de rotation des AX12 (je crois entre 0 et 1023, pas sûr)
#define AX_SPEED                1000


typedef Serial<0> serial_PC_;
typedef Serial<1> serial_AX_;

typedef AX<serial_AX_> AX12;

int main(int argc, char const *argv[])
{
    serial_AX_::init();
    serial_AX_::change_baudrate(BAUD_RATE_SERIE);

    serial_PC_::init();
    
    AX12 AX12_A_RESET(ID_AX, AX_ANGLECW, AX_ANGLECCW);

    AX12_A_RESET.reanimationMode((uint16_t)BAUD_RATE_SERIE);

    
    return 0;
}








