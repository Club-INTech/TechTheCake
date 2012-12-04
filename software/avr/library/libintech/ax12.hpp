#ifndef DEF_AX12_HPP
#define DEF_AX12_HPP

// Librairie Standard
#include <avr/interrupt.h>
#include <avr/io.h>
#include <util/delay.h>

#include <libintech/utils.h>

#define AX_BROADCAST            0xFE        // Utilise le code 0xFE pour envoyer à tous les AX12

/** EEPROM AREA **/
#define AX_MODEL_NUMBER_L           0
#define AX_MODEL_NUMBER_H           1
#define AX_VERSION                  2
#define AX_ID                       3
#define AX_BAUD_RATE                4
#define AX_RETURN_DELAY_TIME        5
#define AX_CW_ANGLE_LIMIT_L         6
#define AX_CW_ANGLE_LIMIT_H         7
#define AX_CCW_ANGLE_LIMIT_L        8
#define AX_CCW_ANGLE_LIMIT_H        9
#define AX_SYSTEM_DATA2             10
#define AX_LIMIT_TEMPERATURE        11
#define AX_DOWN_LIMIT_VOLTAGE       12
#define AX_UP_LIMIT_VOLTAGE         13
#define AX_MAX_TORQUE_L             14
#define AX_MAX_TORQUE_H             15
#define AX_RETURN_LEVEL             16
#define AX_ALARM_LED                17
#define AX_ALARM_SHUTDOWN           18
#define AX_OPERATING_MODE           19
#define AX_DOWN_CALIBRATION_L       20
#define AX_DOWN_CALIBRATION_H       21
#define AX_UP_CALIBRATION_L         22
#define AX_UP_CALIBRATION_H         23

/** RAM AREA **/
#define AX_TORQUE_ENABLE            24
#define AX_LED                      25
#define AX_CW_COMPLIANCE_MARGIN     26
#define AX_CCW_COMPLIANCE_MARGIN    27
#define AX_CW_COMPLIANCE_SLOPE      28
#define AX_CCW_COMPLIANCE_SLOPE     29
#define AX_GOAL_POSITION_L          30
#define AX_GOAL_POSITION_H          31
#define AX_GOAL_SPEED_L             32
#define AX_GOAL_SPEED_H             33
#define AX_TORQUE_LIMIT_L           34
#define AX_TORQUE_LIMIT_H           35
#define AX_PRESENT_POSITION_L       36
#define AX_PRESENT_POSITION_H       37
#define AX_PRESENT_SPEED_L          38
#define AX_PRESENT_SPEED_H          39
#define AX_PRESENT_LOAD_L           40
#define AX_PRESENT_LOAD_H           41
#define AX_PRESENT_VOLTAGE          42
#define AX_PRESENT_TEMPERATURE      43
#define AX_REGISTERED_INSTRUCTION   44
#define AX_PAUSE_TIME               45
#define AX_MOVING                   46
#define AX_LOCK                     47
#define AX_PUNCH_L                  48
#define AX_PUNCH_H                  49

/** Instruction Set **/
#define AX_PING                     1
#define AX_READ_DATA                2
#define AX_WRITE_DATA               3
#define AX_REG_WRITE                4
#define AX_ACTION                   5
#define AX_RESET                    6
#define AX_SYNC_WRITE               131


template<class Serial_AX12, uint32_t baudrate>
class AX
{
private:
	uint8_t id_;

    enum {
        READ_TIMEOUT = 0, READ_SUCCESS = 1
    };
    
    // Méthode pour envoyer un packet lisible par l'AX12
    void sendPacket(uint8_t datalength, uint8_t instruction, uint8_t *data)
    {
        uint8_t checksum = 0;
        Serial_AX12::disable_rx();             //désactiver la série
        Serial_AX12::send_char(0xFF);
        Serial_AX12::send_char(0xFF);
        Serial_AX12::send_char(id_);
        Serial_AX12::send_char(datalength + 2);
        Serial_AX12::send_char(instruction);
        
        checksum += id_ + datalength + 2 + instruction;
        
        for (uint8_t f=0; f<datalength; f++) {
            checksum += data[f];
            Serial_AX12::send_char(data[f]);
        }
        
        Serial_AX12::send_char(~checksum);
        Serial_AX12::enable_rx();                //réactiver la série
    }

    void static sendPacketB(uint8_t datalength, uint8_t instruction, uint8_t *data)
    {
        uint8_t checksum = 0;
        Serial_AX12::disable_rx();             //désactiver la série
        Serial_AX12::send_char(0xFF);
        Serial_AX12::send_char(0xFF);
        Serial_AX12::send_char(0xFE);
        Serial_AX12::send_char(datalength + 2);
        Serial_AX12::send_char(instruction);
        
        checksum += 254 + datalength + 2 + instruction;
        
        for (uint8_t f=0; f<datalength; f++) {
            checksum += data[f];
            Serial_AX12::send_char(data[f]);
        }
        
        Serial_AX12::send_char(~checksum);
        Serial_AX12::enable_rx();                //réactiver la série
    }
    
    /// Ecriture d'une séquence de bits 
    void writeData(uint8_t regstart, uint8_t reglength, uint16_t value) {
        uint8_t data [reglength+1];
        data[0] = regstart;
        data[1] = value&0xFF;
        if (reglength > 1) {data[2] = (value&0xFF00)>>8;}
        sendPacket(reglength+1, AX_WRITE_DATA, data);
    }

    void static writeDataB(uint8_t regstart, uint8_t reglength, uint16_t value) {
        uint8_t data [reglength+1];
        data[0] = regstart;
        data[1] = value&0xFF;
        if (reglength > 1) {data[2] = (value&0xFF00)>>8;}
        sendPacketB(reglength+1, AX_WRITE_DATA, data);
    }
    
public:

	AX(uint8_t id, uint16_t AX_angle_CW, uint16_t AX_angle_CCW)  // Constructeur de la classe
	{
		id_ = id;
        // Active l'asservissement du servo
        writeData (AX_TORQUE_ENABLE, 1, 1);
        // Définit les angles mini et maxi
        writeData (AX_CW_ANGLE_LIMIT_L, 2, AX_angle_CW);
        writeData (AX_CCW_ANGLE_LIMIT_L, 2, AX_angle_CCW);
	}

    AX(uint8_t id)  // Constructeur de la classe pour faire tourner l'AX12 en continu
    {
        id_ = id;
        // Active l'asservissement du servo
        writeData (AX_TORQUE_ENABLE, 1, 1);
    }
    
    /// Reset de l'AX12
    void reset() {
        uint8_t *data = 0;
        sendPacket(0, AX_RESET, data);  
    }
    
    /// Tente de réanimer un AX12 mort.
    void reanimationMode(uint8_t id = 0xFE)
    {
        uint8_t debug_baudrate = 0;
        // On brute-force le baud rate des AX12, et on leur envoie pour chaque baud rate
        // d'écoute un signal de reset.
        while (debug_baudrate < 0xFF)
        {
            Serial_AX12::change_baudrate(2000000/(debug_baudrate + 1));
            writeData(AX_BAUD_RATE, 1, 9600);
            debug_baudrate++;
        }
        
        // Une fois que le signal de reset a été reçu, l'AX12 écoute à 1.000.000 bps.
        // Donc à ce baud rate, on reflash le baud rate d'écoute de l'AX12.

        //writeData(0xFE, AX_BAUD_RATE, 1, uint8_t(2000000/baud_rate - 1));
        
        //Serial_AX12::change_baudrate(baud_rate);
        // Si l'id est différente du broadcast, alors on la reflash.
    }
    
    /// Réinitialisation de l'ID de l'AX12
    void initID(uint8_t nouvel_id)
    {
        writeData(AX_ID, 1, nouvel_id);
    }
    
    /// Goto - Envoyer un angle en DEGRES entre angleMin et angleMax
    void goTo(uint16_t angle)
    {
        writeData(AX_GOAL_POSITION_L, 2, (uint16_t)(1023.*angle/300.));
    }

    void static goToB(uint16_t angle)
    {
        writeDataB(AX_GOAL_POSITION_L, 2, (uint16_t)(1023.*angle/300.));
    }
    

    /// Changement de l'angle min
    void changeAngleMIN(uint16_t angleCW)
    {
        writeData(AX_CW_ANGLE_LIMIT_L, 2, angleCW);
    }

    void static changeAngleMINB(uint16_t angleCW)
    {
        writeDataB(AX_CW_ANGLE_LIMIT_L, 2, angleCW);
    }


    /// Changement de l'angle max
    void changeAngleMAX(uint16_t angleCCW)
    {
        writeData(AX_CCW_ANGLE_LIMIT_L, 2, angleCCW);
    }

    void static changeAngleMAXB(uint16_t angleCCW)
    {
        writeDataB(AX_CCW_ANGLE_LIMIT_L, 2, angleCCW);
    }
    

    /// Changement de la vitesse de rotation
    void changeSpeed(uint16_t vitesse)
    {
        writeData(AX_GOAL_SPEED_L, 2, 1023.*vitesse/100.);
    }

    void static changeSpeedB(uint16_t vitesse)
    {
        writeDataB(AX_GOAL_SPEED_L, 2, vitesse);
    }


    /// Désasservissement d'un AX12 branché.
    void unasserv()
    {
        writeData(AX_TORQUE_ENABLE, 1, 0);
    }

    void static unasservB()
    {
        writeDataB(AX_TORQUE_ENABLE, 1, 0);
    }


    // Changement de la limite de température
    void changeT(uint8_t temperature)
    {
        writeData(AX_LIMIT_TEMPERATURE, 1, temperature);
    }

    void static changeTB(uint8_t temperature)
    {
        writeDataB(AX_LIMIT_TEMPERATURE, 1, temperature);
    }


    // Changement du voltage maximal
    void changeVMax(uint8_t volt)
    {
        writeData(AX_UP_LIMIT_VOLTAGE, 1, volt);
    }

    void static changeVMaxB(uint8_t volt)
    {
        writeDataB(AX_UP_LIMIT_VOLTAGE, 1, volt);
    }


    // Changement du voltage minimal
    void changeVMin(uint8_t volt)
    {
        writeData(AX_DOWN_LIMIT_VOLTAGE, 1, volt);
    }

    void static changeVMinB(uint8_t volt)
    {
        writeDataB(AX_DOWN_LIMIT_VOLTAGE, 1, volt);
    }


    // LEDs d'alarme
    void led(uint8_t type)
    {
        writeData(AX_ALARM_LED, 1, type);
    }

    void static ledB(uint8_t type)
    {
        writeDataB(AX_ALARM_LED, 1, type);
    }

    // Pour envoyer un message comme un grand !
    void message(uint8_t adresse, uint8_t n, uint16_t val)
    {
        writeData(adresse, n, val);
    }

    void static messageB(uint8_t adresse, uint8_t n, uint16_t val)
    {
        writeDataB(adresse, n, val);
    }
};

#endif
