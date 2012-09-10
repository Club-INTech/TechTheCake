/*
 * File:   serial.hpp
 * Author: philippe
 *
 * Created on 4 février 2012, 19:00
 */

#ifndef SERIAL_HPP
#define SERIAL_HPP

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <string.h>
#include <libintech/singleton.hpp>
#include <stdint.h>

#define rx_buffer__SIZE 32

template<uint8_t id>
class Serial {

private:
    struct ring_buffer
    {
        ring_buffer() {}
        unsigned char buffer[rx_buffer__SIZE] ;
        int head;
        int tail;
    };

    static volatile ring_buffer rx_buffer_;

private:

    static void PLEASE_INCLUDE_SERIAL_INTERRUPT();


    static inline bool available(void)
    {
        return (rx_buffer__SIZE + rx_buffer_.head - rx_buffer_.tail) % rx_buffer__SIZE;
    }

    static inline void send_ln()
    {
        send_char('\r');
        send_char('\n');
    }

    static inline unsigned char read_single_char()
    {
        while(!available()) {}
        unsigned char c = rx_buffer_.buffer[rx_buffer_.tail];
        rx_buffer_.tail = (rx_buffer_.tail + 1) % rx_buffer__SIZE;
        return c;
    }

public:

    /**
     * Initialise la liaison série (registres)
     * 
     */
    static inline void init();

    /**
     * Fixe le baudrate (défaut à 57600)
     * 
     */
    static inline void change_baudrate(uint32_t BAUD_RATE);

    /**
     * Envoie un caractère sur TX
     * 
     */
    static inline void send_char(unsigned char byte);

    /**
     * Enregistre un caractère dans le buffer, appelée par les interruptions sur RX
     * 
     */
    static inline void store_char(unsigned char c)
    {
        int i = (rx_buffer_.head + 1) % rx_buffer__SIZE;
        if (i != rx_buffer_.tail)
        {
            rx_buffer_.buffer[rx_buffer_.head] = c;
            rx_buffer_.head = i;
        }
    }

    /**
     * Envoie une chaine correspondant à la valeur binaire du paramètre
     * 
     */
    template<class T>
    static inline void print_binary(T val)
    {
        static char buff[sizeof(T) * 8 + 1];
        buff[sizeof(T) * 8]='\0';
        int16_t j = sizeof(T) * 8 - 1;
        for(int16_t i=0 ; i<sizeof(T)*8 ; ++i)
        {
            if(val & ((T)1 << i))
               buff[j] = '1';
            else
               buff[j] = '0';
            j--;
        }
        print((const char *)buff);
    }

    static inline void print_binary(unsigned char * val, int16_t len)
    {
        for(int16_t i = 0 ; i<len ; ++i)
        {
            print_binary(val[i]);
        }
    }

    /**
     * Envoie sur la liaison série, sans retour à la ligne \n (pour communications entre AVR)
     * 
     */
    template<class T>
    static inline void print_noln(T val)
    {
        char buffer[10];
        ltoa(val,buffer,10);
        print_noln((const char *)buffer);
    }

    static inline void print_noln(char val)
    {
        send_char(val);
        send_char('\r');
    }

    static inline void print_noln(unsigned char val)
    {
        send_char(val);
        send_char('\r');
    }
    
    static inline void print_noln(bool val)
    {
        (val) ? print_noln("true") : print_noln("false");
        send_char('\r');
    }

    static inline void print_noln(char* val)
    {
        for(uint16_t i = 0 ; i < strlen(val) ; i++)
        {
            send_char(val[i]);
        }
        send_char('\r');
    }
    
    static inline void print_noln(const char* val)
    {
        for(uint16_t i = 0 ; i < strlen(val) ; i++)
        {
            send_char(val[i]);
        }
        send_char('\r');
    }

    /**
     * Envoie sur la liaison série, avec retour à la ligne \n
     * 
     */
    template<class T>
    static inline void print(T val)
    {
        print_noln(val);
        send_char('\n');
    }
    
    // READ INT8_t
    static inline void read(int8_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }

    // READ UINT8_t
    static inline void read(uint8_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }
    
    // READ INT16_t
    static inline void read(int16_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }
    
    // READ UINT16_t
    static inline void read(uint16_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }
    
    // READ INT32_t
    static inline void read(int32_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }
    
    // READ UINT32_t
    static inline void read(uint32_t& valeur){
        static char buffer[20];
        read(buffer);
        valeur = atol(buffer);
    }    

    // READ FLOAT
    static inline void read(float &valeur)
    {
        static char buffer[20];
        read(buffer);
        valeur = atof(buffer);
    }
    
    /**
     * Ecoute sur la liaison série, l'appel est bloquant jusqu'à la réception du délimiteur \r
     * 
     */
    static inline uint8_t read(char* string)
    {
        uint8_t i = 0;
        
        // Ecoute jusqu'à réception du délimiteur \r
        do
        {
            string[i] = static_cast<char>(read_single_char());
            i++;
        }
        while(string[i-1] != '\r');
        
        // Remplace le délimiteur par une fin de chaine
        string[i-1] = '\0';
        
        // Retourne la taille de la chaine lue
        return i-1;
    }
    
    static inline uint8_t read(unsigned char* string, uint8_t length)
    {
        uint8_t i = 0;
        for (; i < length; i++)
        {
            unsigned char tmp = read_single_char();
            if(tmp == '\r')
            {
                return i;
            }
            
            string[i] = tmp;
        }
        
        return i;
    }

    // READ STRING
    static inline uint8_t read(char* string, uint8_t length){
        uint8_t i = 0;
        for (; i < length; i++){
            while(!available()){ asm("nop"); }
            char tmp = static_cast<char>(read_single_char());
            if(tmp == '\r'){
                return i;
        }
            string[i] = tmp;
        }
        return i;
    }
};


template<uint8_t ID>
volatile typename Serial<ID>::ring_buffer Serial<ID>::rx_buffer_;

#endif  /* SERIAL_HPP */


