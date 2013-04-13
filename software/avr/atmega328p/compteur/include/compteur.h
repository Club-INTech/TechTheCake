#ifndef COMPTEUR_H
#define COMPTEUR_H

#include <stdint.h>
#include <avr/io.h>
#include <avr/interrupt.h>

#include "twi_slave.h"

/*
 *  Pins des codeurs
 */
#define CODEUR11    (1 << PORTB0)
#define CODEUR12    (1 << PORTB1)
#define CODEUR21    (1 << PORTD6)
#define CODEUR22    (1 << PORTD7)

/*
 *  Position roues
 */
extern volatile int32_t roue1;
extern volatile int32_t roue2;

/*
 *  Initialisations
 *    interruptions codeurs roues
 */
void compteur_init (void);

#endif
