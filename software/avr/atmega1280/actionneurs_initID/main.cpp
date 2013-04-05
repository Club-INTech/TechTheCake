// ATTENTION, NE FONCTIONNE PAS!!
//
//
//
//
//
//
//
//
//
//
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
#define ID_AX 					4



// Le reste des constantes est inutile
#define BAUD_RATE_SERIE         9600

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
    
    AX12 ax12_a_reset(ID_AX, AX_ANGLECW, AX_ANGLECCW);

	while (1)
	{
		ax12_a_reset.goTo(90);
		_delay_ms(900);
		ax12_a_reset.goTo(100);
		_delay_ms(900);
	}

    
    return 0;
}
