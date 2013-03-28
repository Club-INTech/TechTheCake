#include "communication.h"

Communication::Communication()
{
	sei();
	TWI_Init();
}

void Communication::envoyer()
{
	TWI_Loop();
}
