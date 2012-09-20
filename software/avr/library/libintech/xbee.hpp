/* 
 * File:   xbee.hpp
 * Author: marc
 *
 * Created on 21 septembre 2012, 00:04
 */

#ifndef XBEE_HPP
#define	XBEE_HPP

template<class Serial>
class Xbee {
private:
    static volatile bool busy;

public:

    static void init() {
        Serial::init();
    }
    
    static inline void send(uint16_t address, char* message) {
        uint8_t checksum = 0;
        uint16_t length = strlen(message) + 5;
        
        // Délimiteur
        Serial::send_char(0x7E);
        
        // Taille du message
        Serial::send_char(length >> 8);
        Serial::send_char((length << 8) >> 8);
        
        // API identifier: Request TX 16 bits
        Serial::send_char(0x01);
        checksum += 1;
        
        // API Frame ID: 0 (aucun ACK)
        Serial::send_char(0x00);
        
        // Adresse de destination
        Serial::send_char(address >> 8);
        checksum += address >> 8;
        Serial::send_char((address << 8) >> 8);
        checksum += (address << 8) >> 8;
        
        // Option
        Serial::send_char(0x00);
        
        // Message
        for (uint16_t i = 0; i < strlen(message); i++) {
            Serial::send_char(message[i]);
            checksum += message[i];
        }
        
        // Checksum
        Serial::send_char(0xFF - checksum);
    }
    
    static inline void read(char* message) {
        uint8_t checksum = 0;
        uint8_t buffer;
        uint16_t length;
        uint16_t source_address;
        uint8_t signal_strength;
        
        // Délimiteur de trame
        do {
            Serial::read_char(buffer);
        }
        while(buffer != 0x7E);
        
        // Taille de la réponse
        Serial::read_char(buffer);
        length = buffer << 8;
        Serial::read_char(buffer);
        length += buffer;
        
        // Type de réponse (ignoré pour le moment)
        Serial::read_char(buffer);
        
        // Adresse de l'emetteur
        Serial::read_char(buffer);
        source_address = buffer << 8;
        Serial::read_char(buffer);
        source_address += buffer;
        
        // Force du signal
        Serial::read_char(signal_strength);
        
        // Options (ignoré pour le moment)
        Serial::read_char(buffer);
        
        for (uint8_t i = 0; i < length - 5; i++) {
             Serial::read_char(buffer);
             message[i] = buffer;
        }
        
        // Checksum (ignoré pour le moment)
        Serial::read_char(buffer);
    }


};

#endif

