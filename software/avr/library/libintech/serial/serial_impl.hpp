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

public:

    enum { READ_TIMEOUT = 0, READ_SUCCESS = 1 };
    
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
     * Envoie un caractère sur TX (pas de conversion ASCII)
     * 
     */
    static inline void send_char(unsigned char byte);
    
    /**
     * Récupère un caractère sur RX (pas de conversion ASCII)
     * 
     * @param   byte    Char récupéré sur RX
     * @param   timeout Timeout en ms (approximatif)
     * @return  READ_SUCCESS si caractère récupéré ou READ_TIMEOUT si timeout écoulé
     * 
     */
    static inline uint8_t read_char(unsigned char &byte, uint16_t timeout = 0)
    {
        uint16_t i = 0;
        uint8_t j = 0;
        
        // Ajuste le timeout pour faire correspondre approximativement à des ms
        if (timeout > 0) timeout *= 2.5;
        
        // Attente jusqu'à réception d'un caractère
        while(!available())
        {
            if (timeout > 0)
            {
                if (i > timeout) return READ_TIMEOUT;
                if (j == 0) i++;
                j++;
            }
        }
        
        byte = rx_buffer_.buffer[rx_buffer_.tail];
        rx_buffer_.tail = (rx_buffer_.tail + 1) % rx_buffer__SIZE;
        
        return READ_SUCCESS;
    }

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
     * Affiche un retour à la ligne
     * 
     */
    static inline void send_ln()
    {
        send_char('\r');
        send_char('\n');
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
        uint16_t j = sizeof(T) * 8 - 1;
        for(uint16_t i = 0; i < sizeof(T) * 8; ++i)
        {
            if(val & ((T)1 << i))
               buff[j] = '1';
            else
               buff[j] = '0';
            j--;
        }
        print((const char *)buff);
    }

    static inline void print_binary(unsigned char *val, int16_t len)
    {
        for(int16_t i = 0 ; i < len ; ++i)
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
    
    /**
     * Lecture d'un int
     * 
     */
    template<class T>
    static inline uint8_t read(T &val, uint16_t timeout = 0){
        static char buffer[20];
        uint8_t status = read(buffer, timeout);
        val = atol(buffer);
        
        return status;
    }
    
    /**
     * Lecture d'un float
     * 
     */
    static inline uint8_t read(float &val, uint16_t timeout = 0)
    {
        static char buffer[20];
        uint8_t status = read(buffer, timeout);
        val = atof(buffer);
        
        return status;
    }
    
    /**
     * Ecoute sur la liaison série, l'appel est bloquant jusqu'à la réception du délimiteur \r
     * 
     */
    static inline uint8_t read(char* string, uint16_t timeout = 0)
    {
        static unsigned char buffer;
        uint8_t i = 0;
        
        // Ecoute jusqu'à réception du délimiteur \r
        do
        {
            // Tentative de lecture, abandonne si timeout
            if (read_char(buffer, timeout) == READ_TIMEOUT) return READ_TIMEOUT;
            
            // Uniquement \r (= entrée), renvoie le message précédent
            if (i == 0 && buffer == '\r')
            {
                return READ_SUCCESS;
            }
            
            // Ignore le premier caractère si \n
            // Permet de faire des print entre AVR
            if (i == 0 && buffer == '\n')
            {
                continue;
            }
            
            string[i] = static_cast<char>(buffer);
            i++;
        }
        while(string[i-1] != '\r');
        
        // Remplace le délimiteur par une fin de chaine
        string[i-1] = '\0';
        
        return READ_SUCCESS;
    }
    
};


template<uint8_t ID>
volatile typename Serial<ID>::ring_buffer Serial<ID>::rx_buffer_;

#endif  /* SERIAL_HPP */


