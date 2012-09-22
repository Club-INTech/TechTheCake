/* 
 * File:   xbee.hpp
 * Author: marc
 *
 * Created on 21 septembre 2012, 00:04
 */

#ifndef XBEE_HPP
#define	XBEE_HPP

template<class Serial, class Debug>
class Xbee {
public:

    static void init() {
        Serial::init();
        Debug::init();
    }

    /**
     * Envoie un message à un module
     * 
     * - Aucun ACK demandé pour simplifier
     * - Pas de gestion des caractères spéciaux :
     *    - 0x7E: ~
     *    - 0x7D: }
     *    - 0x11: XON
     *    - 0x13: XOFF
     * 
     * @param address   Adresse du destinataire
     * @param message   Message à envoyer
     */
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

    /**
     * Lecture d'un message
     * 
     * @param message   Variable où sera stocké le message après réception
     */
    static inline void read(char* message, uint16_t &source_address, uint8_t &signal_strength) {
        uint8_t checksum = 0;
        uint8_t buffer;
        uint16_t length;

        // Délimiteur de trame
        do {
            Serial::read_char(buffer);
        } while (buffer != 0x7E);

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
        Serial::read_char(checksum);
    }
    
    static inline void read(char* message) {
        uint16_t source_address;
        uint8_t signal_strength;
        read(message, source_address, signal_strength);
    }

    /**
     * Retourne les addresses des modules connectés au réseau dans le tableau response (prévoir de la place)
     * 
     * NON FONCTIONNEL POUR LE MOMENT
     * 
     * @param address   Adresse du destinataire
     * @param message   Message à envoyer
     */
    /*
    static inline uint8_t node_discover(uint16_t* response) {

        // Délimiteur
        Serial::send_char(0x7E);

        // Taille du message
        Serial::send_char(0x00);
        Serial::send_char(0x04);

        // API identifier: AT command
        Serial::send_char(0x08);

        // API Frame ID: 0 (aucun ACK)
        Serial::send_char(0x00);

        // Commande ND: node discover
        Serial::send_char(0x4E);
        Serial::send_char(0x44);

        // Checksum
        Serial::send_char(0x65);

        // Traitement de la réponse...
        uint8_t buffer;
        uint16_t frame_length;
        uint8_t address_number = 0;

        // Réception des modules jusqu'à la frame de fin de transmission
        do {
            // Délimiteur de trame
            do {
                Serial::read_char(buffer);
            } while (buffer != 0x7E);

            // Taille de la réponse
            Serial::read_char(buffer);
            frame_length = buffer << 8;
            Serial::read_char(buffer);
            frame_length += buffer;

            // Length == 1: fin de transmission
            if (frame_length == 1) break;

            // Type de réponse (ignoré pour le moment)
            Serial::read_char(buffer);

            // Frame ID (ignoré pour le moment)
            Serial::read_char(buffer);

            // AT Command (ignoré pour le moment)
            Serial::read_char(buffer);
            Serial::read_char(buffer);

            // Status response (ignoré pour le moment)
            Serial::read_char(buffer);

            uint16_t address = 0;
            
            // Contenu de la réponse
            for (uint8_t i = 0; i < frame_length - 5; i++) {
                Serial::read_char(buffer);
            }
            
            // Stocke l'adresse lue
            response[address_number] = address; 
            address_number++;

        } while (1);
        
        return address_number;
    }
    */

};

#endif

