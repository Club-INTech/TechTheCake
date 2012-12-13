#include <stdint.h>
#include "actionneurs.h"

int main() 
{
    Actionneurs &actionneurs = Actionneurs::Instance();
    
    while(1)
    {
        char buffer[20];
        Actionneurs::serie::read(buffer);
        actionneurs.execute(buffer);
    }
}
