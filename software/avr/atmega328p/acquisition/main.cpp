#include <libintech/codeuse.hpp>
#include <libintech/register.hpp>
#include <avr/interrupt.h>
#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <util/delay.h>

typedef Codeuse< AVR_PORTD <PORTD2>,AVR_PORTD <PORTD3> > codeuse;
typedef Serial<0> serialPC;
typedef Serial<1> serialAsserv;
codeuse c;

//préscalaires à fixer
typedef Timer<0,0> dire_position;
typedef Timer<1,64> arreter_essai; 

void lancer_test(int p, int d, int i){
    
}

int main()
{
    char buffer[10];
    int p,d,i;
        
	sei();
    
    //initialisation des séries
	serialPC::init();
    serialAsserv::init();
    serialAsserv::print("?");
    serialAsserv::read(buffer);

    _delay_ms(5);//on laisse le temps à l'autre de démarrer
    if ( !strcmp( buffer, "0" ) )
        serialPC::print("echec du ping");
    
    //initialisation des timers
    dire_position::init();
    dire_position::disable();//en espérant qu'il ne balance rien avant ;-)
    arreter_essai::init();
    arreter_essai::disable();
	
    //boucle de lecture des ordres
	while(1)
	{
		serialPC::read(buffer);
        if( strcmp( buffer, "kp" ){
            serialPC::read(p);
        }else if(strcmp( buffer, "kd" ){
            serialPC::read(d);        
        }else if(strcmp( buffer, "ki" ){
            serialPC::read(i);
        }else if(strcmp( buffer, "go" ){
            lancer_test(p,d,i);
        }
	}
	return 0;
}

ISR (PCINT2_vect)
{
		c.interruption();
}

ISR(TIMER0_OVF_vect){
    serialPC::print(c.compteur());
}

ISR(TIMER1_OVF_vect){
    dire_position::disable();
    serialPC::write("_");
}
