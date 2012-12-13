#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>

int main() 
{
    //Actionneurs &actionneurs = Actionneurs::Instance();
    
    while(1)
    {
        char buffer[20];
        //Actionneurs::serie::read(buffer);
        //actionneurs.execute(buffer);
    }
    
    return 0;
}
