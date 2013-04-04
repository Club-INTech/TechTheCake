#include "communication.h"

int main( void )
{

	Communication &communication = Communication::Instance();

	while(1)
	{
		communication.envoyer();
	}

	return 0;

}

ISR (PCINT2_vect)
{
	Communication &communication = Communication::Instance();
	communication.codeuseMoteurAvant.interruption();
	communication.codeuseMoteurArriere.interruption();
}
