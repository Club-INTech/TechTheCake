#include <libintech/serial/serial_0_interrupt.hpp>
#include <libintech/serial/serial_0.hpp>
#include <libintech/utils.h>
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
    
    // Envoie une chaine
    char string[10] = "char*";
    Serial<0>::print(string);
        
    _delay_ms(500);

    // Envoie un char (code ASCII 97)
    unsigned char uint8 = 'a';
    Serial<0>::send_char(uint8);
    Serial<0>::send_ln();
        
    _delay_ms(500);
    
    // Envoie un uint8_t
    Serial<0>::print(uint8);
    
    _delay_ms(500);
    
    // Envoie un int 8 bit négatif
    int8_t int8 = -8;
    Serial<0>::print(int8);
        
    _delay_ms(500);
    
    // Envoie un int 16 bits
    uint16_t uint16 = 1616;
    Serial<0>::print(uint16);
    
    _delay_ms(500);
    
    // Envoie un int 16 bits négatif
    int16_t int16 = -1616;
    Serial<0>::print(int16);
    
    _delay_ms(500);
    
    // Envoie un int 32 bits
    uint32_t uint32 = 32323232;
    Serial<0>::print(uint32);
    
    _delay_ms(500);
    
    // Envoie un int 32 bits négatif
    int32_t int32 = -32323232;
    Serial<0>::print(int32);
    
    _delay_ms(500);
        
    // Envoie un booléen
    bool test = true;
    Serial<0>::print(test);
        
    _delay_ms(500);

    // Envoie un entier en binaire
    uint8_t binary = 0;
    Serial<0>::print_binary(binary);
    
    _delay_ms(500);
    
    // Envoie un entier en binaire
    binary = 255;
    Serial<0>::print_binary(binary);
        
    _delay_ms(500);
    Serial<0>::print("-----------");
    _delay_ms(500);
    
    // ------------------
    // Test des read
    // ------------------
    
    while(1)
    {
        // Réception d'une chaine
        Serial<0>::print("string:");
        char buffer[10];
        if (Serial<0>::read(buffer, 3000) == Serial<0>::READ_TIMEOUT) Serial<0>::print("timeout");
        else Serial<0>::print(buffer);
        
        // Réception d'un float
        Serial<0>::print("float (renvoie x1000):");
        float float_val;
        Serial<0>::read(float_val);
        Serial<0>::print(float_val * 1000);
        
        // Réception d'un int8
        Serial<0>::print("int 8 bits:");
        int8_t int8_val;
        if (Serial<0>::read(int8_val, 3000) == Serial<0>::READ_TIMEOUT) Serial<0>::print("timeout");
        else Serial<0>::print(int8_val);
        
        // Réception d'un int16
        Serial<0>::print("int 16 bits:");
        int16_t int16_val;
        Serial<0>::read(int16_val);
        Serial<0>::print(int16_val);
        
        // Réception d'un int32
        Serial<0>::print("int 32 bits:");
        int32_t int32_val;
        Serial<0>::read(int32_val);
        Serial<0>::print(int32_val);
        
        // Réception d'un octet brut
        Serial<0>::print("octet:");
        unsigned char octet;
        Serial<0>::read_char(octet);
        Serial<0>::send_char(octet);
        Serial<0>::send_ln();
    }
    
    return 0;
}
