#include "capteurs.h"

Capteurs::Capteurs()
{
    timer_capteur_us::init();
    timer_refresh::init();
    
    for(uint8_t i=0; i<TAILLE_BUFFER_ASC; i++)
    {
        bufferAscenseurAvant[i]=0;
        bufferAscenseurArriere[i]=0;
    }

}

void Capteurs::maj()
{
    uint8_t retenueAvant = rbi(PINC,PINC0);
    for(uint8_t i=0; i<TAILLE_BUFFER_ASC; i++)
    {
        uint8_t retenueApres = bufferAscenseurAvant[i]&(1<<7)>>7;
        bufferAscenseurAvant[i] <<= 1;
        bufferAscenseurAvant[i] += retenueAvant;
        retenueAvant = retenueApres;
    }

    retenueAvant = rbi(PINC,PINC1);
    for(uint8_t i=0; i<TAILLE_BUFFER_ASC; i++)
    {
        uint8_t retenueApres = bufferAscenseurArriere[i]&(1<<7)>>7;
        bufferAscenseurArriere[i] <<= 1;
        bufferAscenseurArriere[i] += retenueAvant;
        retenueAvant = retenueApres;
    }
}

uint8_t Capteurs::ascenseur_avant()
{
    uint8_t etat = 0;
    for(uint8_t i=0; i<TAILLE_BUFFER_ASC; i++)
        etat |= bufferAscenseurAvant[i];
    return etat;
}

uint8_t Capteurs::ascenseur_arriere()
{
    uint8_t etat = 0;
    for(uint8_t i=0; i<TAILLE_BUFFER_ASC; i++)
        etat |= bufferAscenseurArriere[i];
    return etat;
}

