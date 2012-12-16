#ifndef COMPTEUR_H
#define COMPTEUR_H

#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>

/*
 *  Pins des codeurs
 */
#define CODEUR11    (1 << PORTD2)
#define CODEUR12    (1 << PORTD3)
#define CODEUR21    (1 << PORTC1)
#define CODEUR22    (1 << PORTC0)

/*
 *  Position roues
 */
extern volatile int32_t codeuse;

/*
 *  Initialisations
 *    interruptions codeurs roues
 */
void compteur_init (void);

#endif
