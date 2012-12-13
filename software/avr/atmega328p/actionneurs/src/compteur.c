#include "compteur.h"


volatile int32_t codeuse;

volatile uint8_t etat_codeurs;

void compteur_init (void)
{
    // Initialisation interruptions codeurs
    // Masques
    PCMSK2 |= (1 << PCINT19) | (1 << PCINT18);
    PCMSK1 |= (1 << PCINT9) | (1 << PCINT8);
    // Activer les interruptions
    PCICR |= (1 << PCIE2);
    PCICR |= (1 << PCIE1);

    // Initialisation de l'etat des codeurs
    etat_codeurs = (PIND & CODEUR11) | (PIND & CODEUR12) | (PINC & CODEUR21) | (PINC & CODEUR22);
}

/*
 * Gestion des interruptions sur les pins des codeurs
 * On regarde l'evolution des etats et on deduit le sens de rotation
 * Un schema des signaux aide beaucoup pour comprendre le code
 */


// Interruption codeur 1
ISR (PCINT2_vect)
{
        switch ( etat_codeurs & (CODEUR11 | CODEUR12) ) {
        
        case CODEUR11 | CODEUR12 :
            switch ( PIND & (CODEUR11 | CODEUR12) ) {
                case CODEUR12 :
                    codeuse--;
                    break;
                case CODEUR11 :
                    codeuse++;
                    break;
                default :
                    break;
            }
            break;
            
        case CODEUR11 :
            switch ( PIND & (CODEUR11 | CODEUR12) ) {
                case CODEUR11 | CODEUR12 :
                    codeuse--;
                    break;
                case 0 :
                    codeuse++;
                    break;
                default :
                    break;
            }
            break;
            
        case CODEUR12 :
            switch ( PIND & (CODEUR11 | CODEUR12) ) {
                case CODEUR11 | CODEUR12 :
                    codeuse++;
                    break;
                case 0 :
                    codeuse--;
                    break;
                default :
                    break;
            }
            break;
            
        case 0 :
            switch ( PIND & (CODEUR11 | CODEUR12) ) {
                case CODEUR11 :
                    codeuse--;
                    break;
                case CODEUR12 :
                    codeuse++;
                    break;
                default :
                    break;
            }
            break;
            
        default :
            break;
    }
    
    etat_codeurs = (PIND & CODEUR11) | (PIND & CODEUR12) | (PINC & CODEUR21) | (PINC & CODEUR22);
    
}
