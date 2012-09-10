#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <util/delay.h>
#include <avr/io.h>
#include <stdint.h>

int main() 
{
    //Initialisation série
    Serial<0>::init();
    Serial<0>::change_baudrate(9600);
    sei();
    
    // ------------------
    // Test des print
    // ------------------
    /*
    // Envoie une chaine
    char string[10] = "char*";
    Serial<0>::print(string);
        
    _delay_ms(500);

    // Envoie un uint8_t
    // Envoie le caractère ASCI correspondant
    uint8_t uint8 = 123;
    Serial<0>::print(uint8);
        
    _delay_ms(500);
        
    // Envoie un booléen
    bool test = true;
    Serial<0>::print(test);
        
    _delay_ms(500);

    // Envoie un int
    Serial<0>::print(123);
        
    _delay_ms(500);
    Serial<0>::print("-----------");
    _delay_ms(500);
    */
    
    // ------------------
    // Test des read
    // ------------------
    
    while(1)
    {
        // Réception d'une chaine
        Serial<0>::print("string:");
        char buffer[10];
        Serial<0>::read(buffer);
        Serial<0>::print(buffer);
        
        // Réception d'un float
        Serial<0>::print("float:");
        float float_val;
        Serial<0>::read(float_val);
        Serial<0>::print(float_val);
        
        // Réception d'un int
        Serial<0>::print("int:");
        uint8_t uint8_val;
        Serial<0>::read(uint8_val);
        Serial<0>::print(uint8_val);
    }
    
    return 0;
}
