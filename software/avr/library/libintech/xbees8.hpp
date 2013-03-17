/** 
 * Classe de gestion des communications XBEE
 * 
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
 */

#ifndef XBEES8_HPP
#define XBEES8_HPP

#include <stdlib.h>
#include <avr/io.h>
#include <string.h>

template<class Serial>
class XbeeS8 {
public:

	enum {
        READ_TIMEOUT = 0, READ_SUCCESS = 1
    };

    static void init() {
        Serial::init();
    }
    
    static void change_baudrate(uint32_t baudrate) {
        Serial::change_baudrate(baudrate);
    }
    
	
    /**
     * Envoie un message à un module
     * 
     * Aucun ACK demandé pour simplifier
     * 
     * @param address   Adresse du destinataire
     * @param message   Message à envoyer
     * @param strl		Taille du message (calculée automatiquement avec strlen si pas renseignée)
     */
    static inline void send(uint64_t address, char* message, int8_t strl = -1) {
        uint8_t checksum = 0;
        uint16_t length = (strl == -1) ? strlen(message) + 14 : strl + 14;
		
        // Délimiteur
        Serial::send_char(0x7E);

        // Taille du message
        send_with_escape(length >> 8);
        send_with_escape((length << 8) >> 8);

        // Frame type: TX Request
        Serial::send_char(0x10);
        checksum += 0x10;

        // API Frame ID: 0 (aucun ACK)
        Serial::send_char(0x00);

        // Adresse de destination sur 64 bits
        uint64_t mask = (uint64_t) 0xFF << 56;
        uint8_t address_byte = (address & mask) >> 56;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 48;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 40;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 32;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 24;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 16;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = (address & mask) >> 8;
        send_with_escape(address_byte);
        checksum += address_byte;
        
        mask = mask >> 8;
        address_byte = address & mask;
        send_with_escape(address_byte);
        checksum += address_byte;

        // Reserved
        Serial::send_char(0xFF);
        checksum += 0xFF;
        Serial::send_char(0xFE);
        checksum += 0xFE;
        
        // Broadcast radius
        Serial::send_char(0x00);
        
        // Transmit options
        Serial::send_char(0x00);

        // Message
        for (uint16_t i = 0; i < length - 14; i++) {
            send_with_escape(message[i]);
            checksum += message[i];
        }

        // Checksum
        send_with_escape(0xFF - checksum);
    }
    
    static inline void send(uint64_t address, const char* val) {
        send(address, (char *) val);
    }
    
    template<class T>
    static inline void send(uint64_t address, T val) {
		char bytes[5];
		memcpy(bytes, &val, sizeof(T));
        send(address, bytes, sizeof(T));
    }
    
    /**
     * Erreur mystique sur le 0 en 8 bit seulement
     * 
     */
    static inline void send(uint64_t address, uint8_t val) {
		send(address, (uint16_t) val);
    }
    
    static inline void send(uint64_t address, int8_t val) {
		send(address, (int16_t) val);
    }
    
    /**
     * Lecture d'un message
     * 
     * @param message   Variable où sera stocké le message après réception
     */
    static inline uint8_t read(char* message, uint64_t &source_address, uint8_t &signal_strength, uint16_t timeout) {
        uint8_t checksum = 0;
        uint8_t buffer;
        uint16_t length;
        uint8_t status = READ_SUCCESS;

        // Délimiteur de trame
        do{
            status = read_with_escape(buffer, timeout);
            if (status == READ_TIMEOUT) return status;
        } while (status != READ_TIMEOUT && buffer != 0x7E);
        
        // Taille de la réponse
        status = read_with_escape(buffer, 100);
        if (status == READ_TIMEOUT) return status;
        length = buffer << 8;
        
        status = read_with_escape(buffer, 100);
        if (status == READ_TIMEOUT) return status;
        length += buffer;

        // Type de réponse
        read_with_escape(buffer, 100);
        if (buffer != 0x90) return READ_TIMEOUT;

        // Adresse de l'emetteur
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);
        read_with_escape(buffer, 100);

        // Reserved
        Serial::read_char(buffer, 100);
        Serial::read_char(buffer, 100);
        
        // Receive options
        read_with_escape(buffer, 100);

        for (uint8_t i = 0; i < length - 12; i++) {
            read_with_escape(buffer, 100);
            message[i] = buffer;
        }
        
        // Fin de chaine
        message[length - 12] = '\0';

        // Checksum (ignoré pour le moment)
        read_with_escape(checksum, 100);
        
        return READ_SUCCESS;
    }
    
    template<class T>
    static inline uint8_t read(T &val, uint64_t &source_address, uint8_t &signal_strength, uint16_t timeout) {
        static char buffer[5];
        uint8_t status = read(buffer, source_address, signal_strength, timeout);
        memcpy(&val, buffer, sizeof(T));
        return status;
    }
    
    /**
     * Alias read avec juste le timeout
     * 
     */
    static inline uint8_t read(char* message, uint16_t timeout) {
        uint64_t source_address;
        uint8_t signal_strength;
        return read(message, source_address, signal_strength, timeout);
    }
    
    template<class T>
    static inline uint8_t read(T &val, uint16_t timeout) {
        static char buffer[5];
        uint8_t status = read(buffer, timeout);
        memcpy(&val, buffer, sizeof(T));

        return status;
    }
    
    /**
     * Alias read sans timeout, permet de ne pas rester coincé dans une trame invalide
     * 
     */
    static inline uint8_t read(char* message) {
        uint8_t status;
        do {
			status = read(message, 300);
		} while (status == READ_TIMEOUT);
		
		return status;
    }
    
    template<class T>
    static inline uint8_t read(T &val) {
        static char buffer[5];
        uint8_t status = read(buffer);
        memcpy(&val, buffer, sizeof(T));

        return status;
    }
    
private:
	
	static inline void send_with_escape(uint8_t byte) {
		if (byte == 0x7E || byte == 0x7D || byte == 0x11 || byte == 0x13) {
			Serial::send_char(0x7D);
			Serial::send_char(byte ^ 0x20);
		}
		else {
			Serial::send_char(byte);
		}
	}
    
    static inline uint8_t read_with_escape(uint8_t &byte, uint16_t timeout) {
        uint8_t status = Serial::read_char(byte, timeout);
		if (byte == 0x7D && status == READ_SUCCESS) {
            status = Serial::read_char(byte, timeout);
            byte ^= 0x20;
		}
		return status;
	}

};

#endif

