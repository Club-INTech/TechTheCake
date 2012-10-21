/** 
 * Génération de PWM
 * 
 * @author Philippe TILLET phil.tillet@gmail.com
 * @author Marc BLANC-PATIN marc.blancpatin@gmail.com
 * 
 */

#ifndef PWM_HPP
#define PWM_HPP

#include <stdint.h>
#include <avr/io.h>
#include "prescaler.hpp"

/**
 * MODE FAST PWM (PWM classique)
 * 
 */
 
template<uint8_t timer_id, char output>
struct ModeFastPwm;

template<>
struct ModeFastPwm < 0, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR0A = seuil;
    }

    static void set() {
        // Pin OC0A en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD6);
#elif defined (__AVR_ATmega324P__)
        DDRB |= (1 << PORTB3);
#endif

        // Fast PWM
        TCCR0A &= ~(1 << COM0A0);
        TCCR0A |= (1 << COM0A1);
        TCCR0A |= (1 << WGM00);
        TCCR0A |= (1 << WGM01);
        TCCR0B &= ~(1 << WGM02);
    }
};

template<>
struct ModeFastPwm < 0, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR0B = seuil;
    }

    static void set() {
        // Pin OC0B en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD5);
#elif defined (__AVR_ATmega324P__)
        DDRB |= (1 << PORTB4);
#endif

        // Fast PWM
        TCCR0A &= ~(1 << COM0B0);
        TCCR0A |= (1 << COM0B1);
        TCCR0A |= (1 << WGM00);
        TCCR0A |= (1 << WGM01);
        TCCR0B &= ~(1 << WGM02);
    }
};

template<>
struct ModeFastPwm < 1, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR1A = seuil;
    }

    static void set() {
        // Pin OC1A en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB1);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD5);
#endif

        // Fast PWM
        TCCR1A &= ~(1 << COM1A0);
        TCCR1A |= (1 << COM1A1);
        TCCR1A |= (1 << WGM10);
        TCCR1A |= (1 << WGM11);
        TCCR1B &= ~(1 << WGM12);
    }
};

template<>
struct ModeFastPwm < 1, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR1B = seuil;
    }

    static void set() {
        // Pin OC1B en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB2);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD4);
#endif

        // Fast PWM
        TCCR1A &= ~(1 << COM1B0);
        TCCR1A |= (1 << COM1B1);
        TCCR1A |= (1 << WGM10);
        TCCR1A |= (1 << WGM11);
        TCCR1B &= ~(1 << WGM12);
    }
};

template<>
struct ModeFastPwm < 2, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR2A = seuil;
    }

    static void set() {
        // Pin OC2A en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB3);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD7);
#endif

        // Fast PWM
        TCCR2A &= ~(1 << COM2A0);
        TCCR2A |= (1 << COM2A1);
        TCCR2A |= (1 << WGM20);
        TCCR2A |= (1 << WGM21);
        TCCR2B &= ~(1 << WGM22);
    }
};

template<>
struct ModeFastPwm < 2, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR2B = seuil;
    }

    static void set() {
        // Pin OC2B en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD3);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD6);
#endif

        // Fast PWM
        TCCR2A &= ~(1 << COM2B0);
        TCCR2A |= (1 << COM2B1);
        TCCR2A |= (1 << WGM20);
        TCCR2A |= (1 << WGM21);
        TCCR2B &= ~(1 << WGM22);
    }
};

/**
 * MODE CTC
 * 
 */
 
template<uint8_t timer_id, char output>
struct ModeCTC;

template<>
struct ModeCTC < 0, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR0A = seuil;
    }

    static void set() {
        // Pin OC0A en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD6);
#elif defined (__AVR_ATmega324P__)
        DDRB |= (1 << PORTB3);
#endif

        // Mode CTC, toggle
        TCCR0A |= (1 << COM0A0);
        TCCR0A &= ~(1 << COM0A1);
        TCCR0A &= ~(1 << WGM00);
        TCCR0A |= (1 << WGM01);
        TCCR0B &= ~(1 << WGM02);
    }
};

template<>
struct ModeCTC < 0, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR0B = seuil;
    }

    static void set() {
        // Pin OC0B en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD5);
#elif defined (__AVR_ATmega324P__)
        DDRB |= (1 << PORTB4);
#endif

        // Mode CTC, toggle
        TCCR0A |= (1 << COM0B0);
        TCCR0A &= ~(1 << COM0B1);
        TCCR0A &= ~(1 << WGM00);
        TCCR0A |= (1 << WGM01);
        TCCR0B &= ~(1 << WGM02);
    }
};

template<>
struct ModeCTC < 1, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR1A = seuil;
    }

    static void set() {
        // Pin OC1A en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB1);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD5);
#endif

        // Mode CTC, toggle
        TCCR1A |= (1 << COM1A0);
        TCCR1A &= ~(1 << COM1A1);
        TCCR1A &= ~(1 << WGM10);
        TCCR1A |= (1 << WGM11);
        TCCR1B &= ~(1 << WGM12);
    }
};

template<>
struct ModeCTC < 1, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR1B = seuil;
    }

    static void set() {
        // Pin OC1B en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB2);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD4);
#endif

        // Mode CTC, toggle
        TCCR1A |= (1 << COM1B0);
        TCCR1A &= ~(1 << COM1B1);
        TCCR1A &= ~(1 << WGM10);
        TCCR1A |= (1 << WGM11);
        TCCR1B &= ~(1 << WGM12);
    }
};

template<>
struct ModeCTC < 2, 'A' > {

    static void seuil(uint8_t seuil) {
        OCR2A = seuil;
    }

    static void set() {
        // Pin OC2A en output
#if defined (__AVR_ATmega328P__)
        DDRB |= (1 << PORTB3);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD7);
#endif

        // Mode CTC, toggle
        TCCR2A |= (1 << COM2A0);
        TCCR2A &= ~(1 << COM2A1);
        TCCR2A &= ~(1 << WGM20);
        TCCR2A |= (1 << WGM21);
        TCCR2B &= ~(1 << WGM22);
    }
};

template<>
struct ModeCTC < 2, 'B' > {

    static void seuil(uint8_t seuil) {
        OCR2B = seuil;
    }

    static void set() {
        // Pin OC2B en output
#if defined (__AVR_ATmega328P__)
        DDRD |= (1 << PORTD3);
#elif defined (__AVR_ATmega324P__)
        DDRD |= (1 << PORTD6);
#endif


        // Mode CTC, toggle
        TCCR2A |= (1 << COM2B0);
        TCCR2A &= ~(1 << COM2B1);
        TCCR2A &= ~(1 << WGM20);
        TCCR2A |= (1 << WGM21);
        TCCR2B &= ~(1 << WGM22);
    }
};

/**
 * Classe de gestion des PWM
 * 
 * ID_                  Numéro du timer à utiliser pour générer le PWM
 * MODE_                Mode de fonctionnement (cf datasheet), seul le mode FastPWM est implémenté pour le moment
 * PRESCALER_RATIO_     Prescaler utilisé
 * OUTPUT_              Sortie utilisée pour le PWM (A ou B, correspondant à OCxA ou OCxB)
 * 
 */
template<uint8_t ID_, template<uint8_t, char> class MODE_, uint16_t PRESCALER_RATIO_, char OUTPUT_>
class PWM {
public:
    static const uint8_t ID = ID_;
    static const char OUTPUT = OUTPUT_;
    static const uint16_t PRESCALER_RATIO = PRESCALER_RATIO_;

private:
    typedef Prescaler<ID, PRESCALER_RATIO> prescaler_;
    typedef MODE_<ID_, OUTPUT_> mode_;

public:

    /**
     * Initialise le timer (à appeler obligatoirement pour configurer le timer)
     * 
     */
    static void init() {
        static bool is_init = false;
        if (is_init == false) {
            mode_::set();
            prescaler_::set();
            is_init = true;
        }
    }

    /**
     * Fixe la valeur du PWM
     * 
     * @param   new_value   PWM (0 à 255 pour un timer 8 bit, 0 à 65535 pour un 16 bit)
     * 
     */
    static inline void value(uint16_t new_value) {
        mode_::seuil(new_value);
    }

    /**
     * Désactive la génération du PWM
     * 
     */
    static inline void disable() {
        Prescaler<ID_, 0 > ::set();
    }

    /**
     * Réactive la génération du PWM
     * 
     */
    static inline void enable() {
        prescaler_::set();
    }
};

#endif
