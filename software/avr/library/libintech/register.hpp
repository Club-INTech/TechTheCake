/** 
 * Abstraction des pins AVR pour utilisation par les différentes librairies
 * 
 * @author Philippe TILLET phil.tillet@gmail.com
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
 */

#ifndef REGISTER_HPP_
#define REGISTER_HPP_

#include <stdint.h>
#include <avr/io.h>

/// PORT D
template<uint16_t bit>
struct AVR_PORTD {

    static void set_interrupt() {
        sbi(PCMSK0, bit); // PCINT18 pour PORTC2
        sbi(PCICR, PCIE0);//active PCINT
    }

    static void clear_interrupt() {
       cbi(PCMSK0,bit);
    }

    static void set_input() {
        DDRD &= ~(1 << bit);
    }

    static void set_output() {
        DDRD |= (1 << bit);
    }

    static void set() {
        PORTD |= (1 << bit);
    }

    static void clear() {
        PORTD &= ~(1 << bit);
    }

    static uint8_t read() {
        return ( (PIND & (1 << bit)) >> bit);
    }
};

/// PORT C
template<uint16_t bit>
struct AVR_PORTC {

    static void set_interrupt() {
        sbi(PCMSK0, bit); // PCINT18 pour PORTC2
        sbi(PCICR, PCIE0);//active PCINT
    }

    static void clear_interrupt() {
        cbi(PCMSK0, bit);
    }

    static void set_input() {
        DDRC &= ~(1 << bit);
    }

    static void set_output() {
        DDRC |= (1 << bit);
    }

    static void set() {
        PORTC |= (1 << bit);
    }

    static void clear() {
        PORTC &= ~(1 << bit);
    }

    static uint8_t read() {
        return ( (PINC & (1 << bit)) >> bit);
    }

};

/// PORT B
template<uint16_t bit>
struct AVR_PORTB {

    static void set_interrupt() {
        sbi(PCMSK0, bit);
        sbi(PCICR, PCIE0);
    }

    static void clear_interrupt() {
        cbi(PCMSK0,bit);
    }

    static void set_input() {
        DDRB &= ~(1 << bit);
    }

    static void set_output() {
        DDRB |= (1 << bit);
    }

    static void set() {
        PORTB |= (1 << bit);
    }

    static void clear() {
        PORTB &= ~(1 << bit);
    }

    static uint8_t read() {
        return ( (PINB & (1 << bit)) >> bit);
    }
};

//convertisseur ADC
template<uint16_t bit>
struct AVR_ADC {

    static void enable() {
        ADMUX |= (1 << REFS0); // Set ADC reference to AVCC 
        ADMUX |= (1 << ADLAR); // Left adjust ADC result to allow easy 8 bit reading 

        ADMUX |= bit;   //on choisit le ADC à utiliser

        ADCSRA |= (1 << ADATE);  // Set ADC to Free-Running Mode 
        ADCSRA |= (1 << ADEN);  // Enable ADC 
        ADCSRA |= (1 << ADSC);  // Start A2D Conversions  
    }

    static void disable() {
        ADMUX &= ~(1 << REFS0);
        ADMUX &= ~(1 << ADLAR);
        ADMUX &= ~bit;   //on choisit le ADC à utiliser
        ADCSRA &= ~(1 << ADATE);
        ADCSRA &= ~(1 << ADEN);
        ADCSRA &= ~(1 << ADSC);
    }

    static void prescaler(uint16_t facteur) { //facteurs disponibles: 2, 4, 8, 16, 32, 64 et 128 
        switch(facteur) {
        case 2:  ADCSRA |= (1 << ADPS0);
                 break;
        case 4:  ADCSRA |= (1 << ADPS1);
                 break;
        case 8:  ADCSRA |= (1 << ADPS1) | (1 << ADPS0);
                 break;
        case 16: ADCSRA |= (1 << ADPS2);
                 break;
        case 32: ADCSRA |= (1 << ADPS2) | (1 << ADPS0);
                 break;
        case 64: ADCSRA |= (1 << ADPS2) | (1 << ADPS1);
                 break;
        case 128: ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
                 break;
        }
    }

};

#endif /* REGISTER_HPP_ */
