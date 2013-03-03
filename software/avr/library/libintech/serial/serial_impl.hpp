/** 
 * Classe de gestion des UART (liaison série)
 * 
 * @author Philippe TILLET phil.tillet@gmail.com
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
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

    struct ring_buffer {

        ring_buffer() {
        }
        unsigned char buffer[rx_buffer__SIZE];
        int head;
        int tail;
    };

    static volatile ring_buffer rx_buffer_;
    static volatile bool acquittement;

private:

    static void PLEASE_INCLUDE_SERIAL_INTERRUPT();

public:

    enum {
        READ_TIMEOUT = 0, READ_SUCCESS = 1
    };

    /**
     * Initialise la liaison série (registres)
     * 
     */
    static inline void init();
    
    /**
     * Active la réception
     * 
     */
    static inline void enable_rx();
    
    /**
     * Désactive la réception
     * 
     */
    static inline void disable_rx();
	
	/**
     * Active la transmission
     * 
     */
    static inline void enable_tx();
    
    /**
     * Désactive la transmission
     * 
     */
    static inline void disable_tx();

    /**
     * Fixe le baudrate (défaut à 57600)
     * 
     */
    static inline void change_baudrate(uint32_t BAUD_RATE);
    
    /**
     * Indique si un message a été reçu ou non
     * 
     */
    static inline bool available(void) {
        return (rx_buffer__SIZE + rx_buffer_.head - rx_buffer_.tail) % rx_buffer__SIZE;
    }

    /**
     * Envoie un octet sur TX (pas de conversion ASCII)
     * 
     */
    static inline void send_char(unsigned char byte);
    
    /**
     * Active ou non l'acquittement à chaque read sur la série
     * 
     */
    static inline void activer_acquittement(bool activation) {
        acquittement = activation;        
    }

    /**
     * Récupère un octet sur RX (pas de conversion ASCII)
     * 
     * @param   byte    Char récupéré sur RX
     * @param   timeout Timeout en ms (approximatif)
     * @return  READ_SUCCESS si caractère récupéré ou READ_TIMEOUT si timeout écoulé
     * 
     */
    static inline uint8_t read_char(unsigned char &byte, uint16_t timeout = 0) {
        uint16_t i = 0;
        uint8_t j = 0;
        
        // Ajuste le timeout pour faire correspondre approximativement à des ms
        // Valable pour 20MHz
        // Si quelqu'un veut améliorer ça...
        if (timeout > 0) timeout *= 3.1;

        // Attente jusqu'à réception d'un caractère
        while (!available()) {
            if (timeout > 0) {
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
    static inline void store_char(unsigned char c) {
        int i = (rx_buffer_.head + 1) % rx_buffer__SIZE;
        if (i != rx_buffer_.tail) {
            rx_buffer_.buffer[rx_buffer_.head] = c;
            rx_buffer_.head = i;
        }
    }

    /**
     * Affiche un retour à la ligne
     * 
     */
    static inline void send_ln() {
        send_char('\r');
        send_char('\n');
    }

    /**
     * Envoie une chaine correspondant à la valeur binaire du paramètre
     * 
     */
    template<class T>
    static inline void print_binary(T val) {
        static char buff[sizeof (T) * 8 + 1];
        buff[sizeof (T) * 8] = '\0';
        uint16_t j = sizeof (T) * 8 - 1;
        for (uint16_t i = 0; i < sizeof (T) * 8; ++i) {
            if (val & ((T) 1 << i))
                buff[j] = '1';
            else
                buff[j] = '0';
            j--;
        }
        print((const char *) buff);
    }

    static inline void print_binary(unsigned char *val, int16_t len) {
        for (int16_t i = 0; i < len; ++i) {
            print_binary(val[i]);
        }
    }

    /**
     * Envoie sur la liaison série, sans retour à la ligne \n (pour communications entre AVR)
     * 
     */
    template<class T>
    static inline void write(T val) {
        char buffer[10];
        ltoa(val, buffer, 10);
        write((const char *) buffer);
    }

    static inline void write(bool val) {
        (val) ? write("true") : write("false");
    }

    static inline void write(char* val) {
        for (uint16_t i = 0; i < strlen(val); i++) {
            send_char(val[i]);
        }
    }

    static inline void write(const char* val) {
        for (uint16_t i = 0; i < strlen(val); i++) {
            send_char(val[i]);
        }
    }
    
    static inline void write(float value, int places) {

		// this is used to cast digits
		int digit;
		float tens = 0.1;
		int tenscount = 0;
		int i;
		float tempfloat = value;

		// make sure we round properly. this could use pow from <math.h>, but doesn't seem worth the import
		// if this rounding step isn't here, the value  54.321 prints as 54.3209
		// calculate rounding term d:   0.5/pow(10,places)
		float d = 0.5;
		if (value < 0)
			d *= -1.0;
		// divide by ten for each decimal place
		for (i = 0; i < places; i++)
			d /= 10.0;
		// this small addition, combined with truncation will round our values properly
		tempfloat += d;

		// first get value tens to be the large power of ten less than value
		// tenscount isn't necessary but it would be useful if you wanted to know after this how many chars the number will take
		if (value < 0)
			tempfloat *= -1.0;
		while ((tens * 10.0) <= tempfloat) {
			tens *= 10.0;
			tenscount += 1;
		}

		// write out the negative if needed
		if (value < 0)
			write("-");

		if (tenscount == 0)
			write(0);

		for (i = 0; i < tenscount; i++) {
			digit = (int) (tempfloat / tens);
			write(digit);
			tempfloat = tempfloat - ((float) digit * tens);
			tens /= 10.0;
		}

		// if no places after decimal, stop now and return
		if (places <= 0)
			return;

		// otherwise, write the point and continue on
		write(".");

		// now write out each decimal place by shifting digits one by one into the ones place and writing the truncated value
		for (i = 0; i < places; i++) {
			tempfloat *= 10.0;
			digit = (int) tempfloat;
			write(digit);
			// once written, subtract off that digit
			tempfloat = tempfloat - (float) digit;
		}
	}
    
    /**
     * Alias pour garder la compatibilité avec les anciens scripts
     * 
     */
    template<class T>
    static inline void print_noln(T val) {
        write(val);
		send_char('\r');
    }

    /**
     * Envoie sur la liaison série, avec délimiteur \r et retour à la ligne \n
     * 
     */
    template<class T>
    static inline void print(T val) {
        write(val);
        send_ln();
    }
    
    /**
     * Envoie d'un float sur la série
     * 
     * @param	val			Valeur à envoyer
     * @param	precision	Précision du float (fait l'arrondi automatiquement)
     * 
     */
    static inline void print(float val, int precision) {
        write(val, precision);
        send_ln();
    }
    
    /**
     * Envoie d'un acquittement
     * 
     */
    static inline void ack() {
        print("_");
    }

    /**
     * Lecture d'un int
     * 
     */
    template<class T>
    static inline uint8_t read(T &val, uint16_t timeout = 0) {
        static char buffer[20];
        uint8_t status = read(buffer, timeout);
        val = atol(buffer);

        return status;
    }

    /**
     * Lecture d'un float
     * 
     */
    static inline uint8_t read(float &val, uint16_t timeout = 0) {
        static char buffer[20];
        uint8_t status = read(buffer, timeout);
        val = atof(buffer);

        return status;
    }

    /**
     * Ecoute sur la liaison série, l'appel est bloquant jusqu'à la réception du délimiteur \r
     * 
     */
    static inline uint8_t read(char* string, uint16_t timeout = 0) {
        static unsigned char buffer;
        uint8_t i = 0;

        // Ecoute jusqu'à réception du délimiteur \r
        do {
            // Tentative de lecture, abandonne si timeout
            if (read_char(buffer, timeout) == READ_TIMEOUT) return READ_TIMEOUT;

            // Uniquement \r (= entrée), renvoie le message précédent
            if (i == 0 && buffer == '\r') {
                if (acquittement) ack();
                return READ_SUCCESS;
            }

            // Ignore le premier caractère si \n
            // Permet de faire des print entre AVR
            if (i == 0 && buffer == '\n') {
                continue;
            }

            string[i] = static_cast<char> (buffer);
            i++;
        } while (string[i - 1] != '\r');

        // Remplace le délimiteur par une fin de chaine
        string[i - 1] = '\0';

        if (acquittement) ack();

        return READ_SUCCESS;
    }

};


template<uint8_t ID>
volatile typename Serial<ID>::ring_buffer Serial<ID>::rx_buffer_;

template<uint8_t ID>
volatile bool Serial<ID>::acquittement;

#endif  /* SERIAL_HPP */


