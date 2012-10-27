#include "balise.h"

Balise::Balise() :
	window_opener(-1),
	distance(0)
{

    // -----------------------
    // Timer
    // -----------------------

    
    offset_timer::init();
    window_timer::init();

    // -----------------------
    // Liaison série
    // -----------------------

    xbee::init();
    xbee::change_baudrate(BAUDRATE);

    // -----------------------
    // Diodes
    // -----------------------

    sbi(DDRC, DDC4);
    sbi(DDRD, DDD2);
    sbi(PORTD, PORTD2);
    

    // -----------------------
    // Interruptions
    // -----------------------

    sei();

    // Pins en input pour les PCINT
    cbi(DDRC, DDC0);
    cbi(DDRC, DDC1);
    cbi(DDRC, DDC2);
    cbi(DDRC, DDC3);

    // Pull up enabled
    sbi(PORTC, PORTC0);
    sbi(PORTC, PORTC1);
    sbi(PORTC, PORTC2);
    sbi(PORTC, PORTC3);

    // Active les interruptions PCINT
    sbi(PCMSK1, PCINT8);
    sbi(PCMSK1, PCINT9);
    sbi(PCMSK1, PCINT10);
    sbi(PCMSK1, PCINT11);
    sbi(PCICR, PCIE1);
}

void Balise::execute(char *order) {
	
    // Ping
    if (strcmp(order,"?") == 0) {
		char p[10] = ".";
        xbee::send(SERVER_ADDRESS, p);
    }
    // Ping
    else if (strcmp(order,"?1") == 0) {
		char p[10] = "/";
        xbee::send(SERVER_ADDRESS, p);
    }
    // Ping
    else if (strcmp(order,"?2") == 0) {
		char p[10] = "0";
        xbee::send(SERVER_ADDRESS, p);
    }
    // Demande de valeur de la dernière distance mesurée
    else if (strcmp(order,"v") == 0) {
        xbee::send(SERVER_ADDRESS, distance);
        xbee::send(SERVER_ADDRESS, offset_timer::value());
    }
    
    // Clock
    else if (strcmp(order,"c") == 0) {
        //xbee::send(SERVER_ADDRESS, synchronisation.clock());
    }
    
    // Synchronisation
    else if (strcmp(order,"s") == 0) {
        //synchronisation.synchroniser_client(SERVER_ADDRESS);
    }
    
    // Latence
    else if (strcmp(order,"l") == 0) {
        xbee::send(SERVER_ADDRESS, 1);
    }
    

    

    
    
}

void Balise::diode_on() {
    sbi(PORTC, PORTC4);
}

void Balise::diode_blink() {
    diode_blink(50, 8);
}

void Balise::diode_blink(uint16_t period, uint8_t number) {
    for (uint8_t i = 1; i <= number; i++) {
        diode_on();
        for (uint16_t i = 1; i <= period; i++) _delay_ms(1);
        diode_off();
        for (uint16_t i = 1; i <= period; i++) _delay_ms(1);
    }
}

void Balise::diode_off() {
    cbi(PORTC, PORTC4);
}

